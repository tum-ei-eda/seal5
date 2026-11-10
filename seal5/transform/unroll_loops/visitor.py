"""Conservative full unrolling for statically bounded behavioral loops."""

from copy import copy

from m2isar.metamodel import behav


def _reference_key(expr):
    if isinstance(expr, behav.NamedReference):
        return expr.reference
    if isinstance(expr, behav.VarDefinition):
        return expr.var
    return None


def _literal_value(expr):
    if not isinstance(expr, behav.Literal):
        return None
    value = expr.value
    try:
        return int(value, expr.base) if isinstance(value, str) else int(value)
    except (TypeError, ValueError):
        return None


def _operator(expr):
    return expr.op.value if isinstance(expr.op, behav.Operator) else expr.op


def evaluate(expr, values):
    """Evaluate the small, side-effect-free subset needed for loop bounds."""
    literal = _literal_value(expr)
    if literal is not None:
        return literal
    if isinstance(expr, behav.NamedReference):
        return values.get(expr.reference)
    if isinstance(expr, (behav.Group, behav.TypeConv)):
        return evaluate(expr.expr, values)
    if isinstance(expr, behav.SliceOperation):
        value = evaluate(expr.expr, values)
        left = evaluate(expr.left, values)
        right = evaluate(expr.right, values)
        if value is None or left is None or right is None or left < right or right < 0:
            return None
        width = left - right + 1
        return (value >> right) & ((1 << width) - 1)
    if isinstance(expr, behav.UnaryOperation):
        right = evaluate(expr.right, values)
        if right is None:
            return None
        return {"+": lambda: right, "-": lambda: -right, "!": lambda: not right, "~": lambda: ~right}.get(
            _operator(expr), lambda: None
        )()
    if not isinstance(expr, behav.BinaryOperation):
        return None
    left, right = evaluate(expr.left, values), evaluate(expr.right, values)
    if left is None or right is None:
        return None
    operations = {
        "+": lambda: left + right,
        "-": lambda: left - right,
        "*": lambda: left * right,
        "/": lambda: left // right if right else None,
        "%": lambda: left % right if right else None,
        "<<": lambda: left << right,
        ">>": lambda: left >> right,
        "&": lambda: left & right,
        "|": lambda: left | right,
        "^": lambda: left ^ right,
        "&&": lambda: bool(left) and bool(right),
        "||": lambda: bool(left) or bool(right),
        "==": lambda: left == right,
        "!=": lambda: left != right,
        "<": lambda: left < right,
        "<=": lambda: left <= right,
        ">": lambda: left > right,
        ">=": lambda: left >= right,
    }
    operation = operations.get(_operator(expr))
    return operation() if operation is not None else None


def _contains_node(expr, node_type):
    if isinstance(expr, node_type):
        return True
    if isinstance(expr, behav.NamedReference):
        return False
    for value in vars(expr).values():
        if isinstance(value, behav.BaseNode) and _contains_node(value, node_type):
            return True
        if isinstance(value, list) and any(
            isinstance(item, behav.BaseNode) and _contains_node(item, node_type) for item in value
        ):
            return True
    return False


def _assigned_keys(expr):
    keys = []
    if isinstance(expr, behav.Assignment):
        key = _reference_key(expr.target)
        if key is not None:
            keys.append(key)
    if isinstance(expr, behav.NamedReference):
        return keys
    for value in vars(expr).values():
        if isinstance(value, behav.BaseNode):
            keys.extend(_assigned_keys(value))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, behav.BaseNode):
                    keys.extend(_assigned_keys(item))
    return keys


def _unconditional_statements(statements):
    """Flatten blocks without crossing conditional control flow."""
    for statement in statements:
        if isinstance(statement, behav.Block):
            yield from _unconditional_statements(statement.statements)
        else:
            yield statement


def _assigned_value(stmt, key, values):
    if not isinstance(stmt, behav.Assignment) or _reference_key(stmt.target) is not key:
        return None
    return evaluate(stmt.expr, values)


def _replace(expr, key, value, assignment_target=False):
    """Shallow-clone an AST, retaining referenced architecture objects."""
    if isinstance(expr, behav.NamedReference):
        if expr.reference is key and not assignment_target:
            return behav.Literal(value, line_info=expr.line_info)
        return copy(expr)
    result = copy(expr)
    if isinstance(expr, behav.Assignment):
        result.target = _replace(expr.target, key, value, assignment_target=True)
        result.expr = _replace(expr.expr, key, value)
        return result
    for name, item in vars(expr).items():
        if isinstance(item, behav.BaseNode):
            # References point into the architecture model and are not AST children.
            if name not in ("reference", "var", "op", "ty"):
                setattr(result, name, _replace(item, key, value))
        elif isinstance(item, list):
            setattr(
                result,
                name,
                [_replace(child, key, value) if isinstance(child, behav.BaseNode) else child for child in item],
            )
    return result


class FullLoopUnroller:
    def __init__(self, max_trip_count=32):
        if max_trip_count < 0:
            raise ValueError("max_trip_count must be non-negative")
        self.max_trip_count = max_trip_count
        self.unrolled = 0

    def run(self, operation):
        operation.statements = self._statements(operation.statements, {})
        return operation

    def _statements(self, statements, values):
        result = []
        for statement in statements:
            if isinstance(statement, behav.Loop):
                replacement = self._loop(statement, values)
                result.extend(replacement if replacement is not None else [self._children(statement, values)])
                continue
            statement = self._children(statement, values)
            result.append(statement)
            if isinstance(statement, behav.Assignment):
                key = _reference_key(statement.target)
                if key is not None:
                    value = evaluate(statement.expr, values)
                    if value is None:
                        values.pop(key, None)
                    else:
                        values[key] = value
        return result

    def _children(self, statement, values):
        if isinstance(statement, behav.Block):
            statement.statements = self._statements(statement.statements, values.copy())
        elif isinstance(statement, behav.Conditional):
            statement.stmts = [
                self._children(branch, values.copy()) if isinstance(branch, behav.Block) else branch
                for branch in statement.stmts
            ]
        return statement

    def _loop(self, loop, values):
        if _contains_node(loop, behav.Break):
            return None
        keys = self._condition_keys(loop.cond)
        if not keys.issubset(values):
            return None
        assigned_keys = _assigned_keys(loop)
        candidates = [key for key in keys if assigned_keys.count(key) == 1]
        if len(candidates) != 1:
            return None
        key = candidates[0]
        if any(condition_key in assigned_keys for condition_key in keys if condition_key is not key):
            return None
        updates = [
            stmt
            for stmt in _unconditional_statements(loop.stmts)
            if isinstance(stmt, behav.Assignment) and _reference_key(stmt.target) is key
        ]
        if len(updates) != 1:
            return None

        current = values[key]
        iterations = []
        for _ in range(self.max_trip_count + 1):
            condition = evaluate(loop.cond, {**values, key: current})
            if not loop.post_test and condition is not True:
                break
            iterations.append(current)
            next_value = _assigned_value(updates[0], key, {**values, key: current})
            if next_value is None or next_value == current:
                return None
            current = next_value
            if loop.post_test and evaluate(loop.cond, {**values, key: current}) is not True:
                break
        else:
            return None
        if len(iterations) > self.max_trip_count:
            return None

        expanded = []
        for value in iterations:
            cloned = [_replace(stmt, key, value) for stmt in loop.stmts]
            iteration_values = {**values, key: value}
            expanded.extend(self._statements(cloned, iteration_values))
        values[key] = current
        self.unrolled += 1
        return expanded

    @staticmethod
    def _condition_keys(expr):
        if isinstance(expr, behav.NamedReference):
            return {expr.reference}
        if isinstance(expr, (behav.Literal, behav.VarDefinition)):
            return set()
        keys = set()
        for value in vars(expr).values():
            if isinstance(value, behav.BaseNode):
                keys.update(FullLoopUnroller._condition_keys(value))
            elif isinstance(value, list):
                for child in value:
                    if isinstance(child, behav.BaseNode):
                        keys.update(FullLoopUnroller._condition_keys(child))
        return keys
