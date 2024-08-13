class DAGNode:
    pass


class DAGLeaf(DAGNode):
    pass


class DAGType(DAGNode):
    def __init__(self, name):
        # print("DAGType")
        assert isinstance(name, str)
        self.name : str = name

    def __repr__(self):
        return self.name


class DAGImm(DAGLeaf):
    def __init__(self, value):
        # print("DAGImm")
        self.value = value

    def __repr__(self):
        return str(self.value)


class DAGOperand(DAGLeaf):
    def __init__(self, name, ty):
        # print("DAGOperand")
        self.name = name
        self.ty : DAGType = ty

    def __repr__(self):
        return f"{self.ty}:${self.name}"


class DAGOperation(DAGNode):
    def __init__(self, name, operands):
        # print("DAGOperation")
        self.name : str = name
        self.operands : list = operands
        assert len(self.operands) > 0

    def __repr__(self):
        return f"({self.name} " + ", ".join(map(str, self.operands)) + ")"


class DAGAssignment(DAGNode):
    def __init__(self, target, expr):
        # print("DAGAssignment")
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"{self.target} <- {self.expr}"


class DAGUnary(DAGOperation):
    def __init__(self, name, right):
        super().__init__(name, [right])


class DAGBinary(DAGOperation):
    def __init__(self, name, left, right):
        super().__init__(name, [left, right])


class DAGTernary(DAGOperation):
    def __init__(self, name, first, second, third):
        super().__init__(name, [first, second, third])


class DAGQuaternary(DAGOperation):
    def __init__(self, name, first, second, third, fourth):
        super().__init__(name, [first, second, third, fourth])
