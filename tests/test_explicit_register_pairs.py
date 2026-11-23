# SPDX-License-Identifier: Apache-2.0
"""Explicit XP views preserve shared storage, parity checks and operand classes."""
from copy import deepcopy
import subprocess
import sys

import pytest
from m2isar.metamodel import arch, behav, type_info

from seal5 import model
from seal5.register_pairs import legal_pair_operation, pair_index_operand
from seal5.transform.collect_register_operands.collect import VisitorContext
from seal5.transform.collect_register_operands.visitor import CollectRegisterOperandsVisitor
from seal5.transform.lower_register_pair_views import LowerRegisterPairViews
from seal5.transform.detect_inouts.collect import VisitorContext as IOContext
from seal5.transform.detect_inouts.utils import IOMode
from seal5.transform.detect_inouts.visitor import DetectInoutsVisitor


def architecture():
    x = arch.RegisterBank("X", 32, type_info.TypeKind.UINT, 32, {})
    xp = arch.RegisterBank("XP", 32, type_info.TypeKind.UINT, 64, {"is_regpair": []})
    field = arch.BitFieldDescr("rs1", 5, type_info.TypeKind.UINT)
    index = behav.NamedReference(field)
    return {"X": x, "XP": xp}, field, behav.IndexedReference(xp, index)


def test_explicit_pair_operand_requires_no_yaml_mapping():
    _, field, pair = architecture()
    operand = model.Seal5Operand("rs1", model.Seal5Type(model.DataType.U, 5, 1), {}, [])
    context = VisitorContext({"rs1": operand})
    CollectRegisterOperandsVisitor().generate(pair, context)
    assert context.operands["rs1"].reg_class == model.Seal5RegisterClass.GPRPair
    assert context.operands["rs1"].reg_ty.width == 64


@pytest.mark.parametrize("bad", ["shift", "slice"])
def test_uncanonical_internal_indices_are_rejected(bad):
    _, field, pair = architecture()
    pair.index = (
        behav.BinaryOperation(behav.NamedReference(field), behav.Operator(">>"), behav.Literal(1))
        if bad == "shift"
        else behav.SliceOperation(behav.NamedReference(field), behav.Literal(4), behav.Literal(1))
    )
    operand = model.Seal5Operand("rs1", model.Seal5Type(model.DataType.U, 5, 1), {}, [])
    with pytest.raises(ValueError, match="XP indices"):
        CollectRegisterOperandsVisitor().generate(pair, VisitorContext({"rs1": operand}))


@pytest.mark.parametrize("shifted", [False, True])
def test_source_uses_encoded_ids_without_remapping(tmp_path, shifted):
    source = tmp_path / "Explicit.core_desc"
    index = "rs1 >> 1" if shifted else "rs1"
    source.write_text(
        """InstructionSet Explicit {
 architectural_state {
  register unsigned<32> X[32] [[is_main_reg]];
  register unsigned<64> XP[32] [[is_regpair]];
 }
 instructions {
  ADD {
   encoding: 7'b0000000 :: rs2[4:0] :: rs1[4:0] :: 3'b000 :: rd[4:0] :: 7'b0001011;
   assembly: {"pair.add", "{name(rd)}, {name(rs1)}, {name(rs2)}"};
   behavior: { XP[rd] = XP["""
        + index
        + """] + XP[rs2]; }
  }
 }
}"""
    )
    result = subprocess.run(
        [sys.executable, "-m", "seal5.frontends.coredsl", str(source), "-o", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    if shifted:
        assert result.returncode != 0
        assert "without shifting" in result.stdout + result.stderr
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        from seal5.model_utils import load_model

        parsed = load_model(tmp_path / "Explicit.m2isarmodel", compat=True)
        assignment = next(iter(parsed.sets["Explicit"].instructions.values())).operation.statements[0]
        while isinstance(assignment, behav.Block):
            assignment = assignment.statements[0]
        assert pair_index_operand(assignment.target.index).reference.name == "rd"


def test_pair_id_parity_checks_are_not_data_inputs():
    _, field, pair = architecture()
    ctx = IOContext()
    ctx.pair_fields = {"rs1"}
    ctx.push(IOMode.READ)
    DetectInoutsVisitor().generate(behav.NamedReference(field), ctx)
    assert not ctx.reads
    DetectInoutsVisitor().generate(pair, ctx)
    assert ctx.reads == {"rs1"}


def test_only_proven_parity_checks_are_specialized():
    _, field, _ = architecture()
    parity = behav.BinaryOperation(behav.NamedReference(field), behav.Operator("&"), behav.Literal(1))
    trap, legal = behav.Block([behav.Break()]), behav.Block([behav.Literal(42)])
    original = behav.Conditional([parity], [trap, legal])
    result = legal_pair_operation(original, {"rs1"})
    assert result.statements[0].value == 42
    assert isinstance(original, behav.Conditional) and original.stmts[0] is trap
    assert isinstance(legal_pair_operation(original, {"rs2"}), behav.Conditional)
    other_bits = deepcopy(original)
    other_bits.conds[0].right = behav.Literal(3)
    assert isinstance(legal_pair_operation(other_bits, {"rs1"}), behav.Conditional)


def evaluate(expr, registers, values):
    if isinstance(expr, behav.Group):
        return evaluate(expr.expr, registers, values)
    if isinstance(expr, behav.TypeConv):
        value = evaluate(expr.expr, registers, values)
        return value & ((1 << expr.size) - 1) if expr.size else value
    if isinstance(expr, behav.ProcedureCall):
        assert expr.ref_or_name.name == "raise"
        raise RuntimeError("illegal instruction")
    if isinstance(expr, behav.Literal):
        return expr.value
    if isinstance(expr, behav.NamedReference):
        return values[expr.reference.name]
    if isinstance(expr, behav.VarDefinition):
        return values[expr.var.name]
    if isinstance(expr, behav.IndexedReference):
        index = evaluate(expr.index, registers, values)
        return registers[index] if index else 0
    if isinstance(expr, behav.BinaryOperation):
        a, b = evaluate(expr.left, registers, values), evaluate(expr.right, registers, values)
        return {
            "<<": lambda: a << b,
            ">>": lambda: a >> b,
            "+": lambda: a + b,
            "|": lambda: a | b,
            "&": lambda: a & b,
            "==": lambda: a == b,
            "!=": lambda: a != b,
        }[expr.op.value]()
    if isinstance(expr, behav.ConcatOperation):
        return (evaluate(expr.left, registers, values) << 32) | evaluate(expr.right, registers, values)
    if isinstance(expr, behav.SliceOperation):
        hi, lo = evaluate(expr.left, registers, values), evaluate(expr.right, registers, values)
        return (evaluate(expr.expr, registers, values) >> lo) & ((1 << (hi - lo + 1)) - 1)
    if isinstance(expr, behav.Ternary):
        return evaluate(expr.then_expr if evaluate(expr.cond, registers, values) else expr.else_expr, registers, values)
    if isinstance(expr, behav.Assignment):
        value = evaluate(expr.expr, registers, values)
        if isinstance(expr.target, behav.IndexedReference):
            index = evaluate(expr.target.index, registers, values)
            if index:
                registers[index] = value
        else:
            ref = expr.target.var if isinstance(expr.target, behav.VarDefinition) else expr.target.reference
            values[ref.name] = value
        return value
    if isinstance(expr, (behav.Block, behav.Operation)):
        for statement in expr.statements:
            evaluate(statement, registers, values)
        return None
    if isinstance(expr, behav.Conditional):
        for i, condition in enumerate(expr.conds):
            if evaluate(condition, registers, values):
                return evaluate(expr.stmts[i], registers, values)
        if len(expr.stmts) > len(expr.conds):
            return evaluate(expr.stmts[-1], registers, values)
        return None
    raise AssertionError(type(expr))


def test_architectural_lowering_preserves_physical_indices_and_zero_pair():
    banks, _, pair = architecture()
    lowered = LowerRegisterPairViews(banks).generate(pair)
    registers = list(range(32))
    registers[1] = 0xFEEDFACE
    for index in range(0, 32, 2):
        result = evaluate(lowered, registers, {"rs1": index})
        expected = 0 if index == 0 else (registers[index + 1] << 32) | registers[index]
        assert result == expected


def test_pair_store_evaluates_aliasing_rhs_once_and_discards_zero_pair():
    banks, _, pair = architecture()
    update = behav.Assignment(pair, behav.BinaryOperation(deepcopy(pair), behav.Operator("+"), behav.Literal(1)))
    lowered = LowerRegisterPairViews(banks).generate(update)
    registers = [0] * 32
    registers[2], registers[3] = 0xFFFFFFFF, 2
    evaluate(lowered, registers, {"rs1": 2})
    assert registers[2:4] == [0, 3]
    before = list(registers)
    evaluate(lowered, registers, {"rs1": 0})
    assert registers == before


def test_full_export_retains_traps_after_compiler_behavior_changes(tmp_path):
    from pathlib import Path
    from seal5.model_utils import load_model, dump_model

    root = Path(__file__).resolve().parents[1]

    def run(module, *args):
        result = subprocess.run([sys.executable, "-m", module, *map(str, args)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr

    run(
        "seal5.frontends.coredsl",
        root / "examples/regpairs/cdsl/RegPairs.core_desc",
        "-I",
        root / "examples/common/cdsl/rv_base",
        "--allow-undefined-const",
        "-o",
        tmp_path,
    )
    path = tmp_path / "RegPairs.seal5model"
    run("seal5.transform.converter", tmp_path / "RegPairs.m2isarmodel", "-o", path)
    parsed = load_model(path)
    pair_set = parsed.sets["XRegPairs"]
    add = next(instr for instr in pair_set.instructions.values() if instr.name == "PAIR_ADD64")
    lowered = LowerRegisterPairViews(pair_set.register_banks, add.vars).generate(deepcopy(add.pair_source_operation))
    for field in ("rd", "rs1", "rs2"):
        registers = list(range(32))
        before = list(registers)
        values = {"rd": 4, "rs1": 2, "rs2": 6}
        values[field] = 31
        with pytest.raises(RuntimeError, match="illegal instruction"):
            evaluate(lowered, registers, values)
        assert registers == before
    # Simulate downstream compiler-only constraint extraction and optimization.
    for instr in pair_set.instructions.values():
        instr.operation = behav.Operation([])
    parsed.sets = {"XRegPairs": pair_set}
    dump_model(parsed, path)
    output = tmp_path / "architectural.core_desc"
    run("seal5.backends.coredsl2.writer", path, "-o", output, "--architectural")
    contents = output.read_text()
    assert contents.count("raise(0, 2)") == len(pair_set.instructions)
    assert "register unsigned<64> XP" not in contents
    assert "XP[" not in contents
    assert "_seal5_pair_value_" in contents
    # The exported shared-storage form must remain valid CoreDSL.
    run("seal5.frontends.coredsl", output, "-o", tmp_path / "reparsed")
