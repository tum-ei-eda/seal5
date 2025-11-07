# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
# Copyright (c) 2025 DLR - Institute of Systems Engineering for Future Mobility
#
#

import argparse
import logging
import pathlib
import time
import random
from typing import Optional, List, Tuple

import pandas as pdf

from mako.template import Template

from m2isar.metamodel import arch

from seal5.index import NamedPatch, File, write_index_yaml
from seal5.utils import is_power_of_two
from seal5.settings import IntrinsicDefn, ExtensionsSettings, Seal5Settings
from seal5.model_utils import load_model
from seal5.riscv_utils import (
    set_bits_in_32bit_val,
    riscv_to_llvm_bytes,
    get_abi_name,
    replace_imm_whole_word_case_insensitive,
)


from .templates import template_dir

logger = logging.getLogger("testcase-generator")


class Operand:
    def __init__(self, name, lower, upper):
        self.name = name
        # self._name = name
        self.lower = lower
        self.upper = upper

    @property
    def length(self):
        return (self.upper - self.lower + 1) if self.upper >= self.lower else (self.lower - self.upper + 1)

    def __repr__(self):
        return f"Operand({self.name}, {self.lower}, {self.upper})"


class EncodingField:
    def __init__(self, name, start, length, value=None, extra=None):
        self.name = name
        self.start = start
        self.length = length

        self.value = value
        self.const = value is not None
        self.extra = extra if extra is not None else value

    def __repr__(self):
        return f"EncodingField({self.name}, {self.start}, {self.length}, {self.value}, {self.const})"


# ----------- Helper functions ------------


def generate_invalid_operand_str(num_operands, operand_str, has_imm_operand):

    # print ("Number of Operands", num_operands)
    # Creating a 2D array

    rows, cols = (num_operands * 2), (num_operands + 1)

    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    op_str = operand_str.split(" , ")

    # Populating the matrix with sample data
    for i in range(rows):
        for j in range(cols):
            if j < num_operands:
                matrix[i][j] = f"{op_str[j]}"
            else:
                matrix[i][j] = f"zero"

    # Set invalid operands
    for cnt in range(rows):
        for op_cnt in range(cols - 1):
            if cnt == op_cnt:
                if "a" not in (op_str[op_cnt]):
                    matrix[cnt][op_cnt] = f"a{op_cnt}"
                else:
                    matrix[cnt][op_cnt] = f"0"

            imm_op_pos = num_operands - 1
            imm_outOfRange_pos = num_operands + 1
            if cnt == imm_outOfRange_pos:
                if has_imm_operand:
                    matrix[cnt][imm_op_pos] = f"-1"
                    matrix[cnt + 1][imm_op_pos] = f"32"
                    matrix[len(matrix) - 1][imm_op_pos] = f"a{num_operands}"

    return matrix


def generate_operand_str(operands, fields, code):
    """
    Generate operand string representations and instruction code matrix,
    especially handling immediate operands with corner cases.
    """
    has_imm_operand = False
    instr_code = code
    instr_op_str = ""
    reg_names_list = ""
    op_str_matrix = []
    instr_code_matrix = []
    llvm_bytes_str_matrix = []
    llvm_bytes_simple_str_matrix = []

    if not operands:
        return "", "", False, [], [], [], []

    op_str_parts = []
    reg_names_parts = []
    imm_bit_len_list = []
    imm_bit_startpos_list = []

    print("fields", fields)
    for operand in operands:
        print("operand", operand, operand.length)

        # Find encoding for operand
        def split_helper(x):
            if "{" in x.name:
                name, rest = x.name.split("{", 1)
                assert rest[-1] == "}"
                rest = rest[:-1].strip().replace(" ", "")
                if "," in rest:
                    raise NotImplementedError
                elif "-" in rest:
                    hi, lo = list(map(int, rest.split("-", 1)))
                    assert hi >= lo
                else:
                    val = int(rest)
                    hi = lo = val
                return x, hi, lo
            else:
                return x, None, None

        enc_fields = [split_helper(f) for f in fields if f.name is not None and f.name.split("{", 1)[0] == operand.name]
        print("enc_fields", enc_fields)
        # input(">>>")

        if len(enc_fields) > 1:
            # TODO: use IS_IMM attr instead!
            assert "imm" in operand.name
            full_value = 0
            for enc_field, hi, lo in enc_fields:
                start_pos = enc_field.start
                bit_len = enc_field.length
                value = random.randint(0, (1 << bit_len) - 1)
                has_imm_operand = True
                mask = (1 << hi) - 1
                full_value |= (value << lo) & mask
                imm_bit_startpos_list.append(str(start_pos))
                imm_bit_len_list.append(str(bit_len))
            op_str_parts.append(str(full_value))
            # imm_bit_len_list.append(str(operand.length))
            # input(">>>")
            # raise NotImplementedError
            continue
        assert len(enc_fields) == 1, f"Encoding field not found for operand {operand.name}"
        enc_field = enc_fields[0]
        enc_field, hi, lo = enc_field
        assert hi is None
        assert lo is None

        start_pos = enc_field.start
        bit_len = enc_field.length

        if "imm" in operand.name:
            value = random.randint(0, (1 << bit_len) - 1)
            has_imm_operand = True
            op_str_parts.append(str(value))
            imm_bit_len_list.append(str(bit_len))
            imm_bit_startpos_list.append(str(start_pos))
            # Instruction code updated later during matrix population
        elif "rd" in operand.name:
            reg_num = random.randint(10, 11)
            instr_code = set_bits_in_32bit_val(instr_code, reg_num, start_pos, bit_len)
            abi_name = get_abi_name(f"x{reg_num}")
            op_str_parts.append(abi_name)
            reg_names_parts.append(f"x{reg_num}")
        elif "rs1" in operand.name:
            reg_num = random.randint(12, 15)
            instr_code = set_bits_in_32bit_val(instr_code, reg_num, start_pos, bit_len)
            abi_name = get_abi_name(f"x{reg_num}")
            op_str_parts.append(abi_name)
            reg_names_parts.append(f"x{reg_num}")
        elif "rs2" in operand.name:
            reg_num = random.randint(15, 17)
            instr_code = set_bits_in_32bit_val(instr_code, reg_num, start_pos, bit_len)
            abi_name = get_abi_name(f"x{reg_num}")
            op_str_parts.append(abi_name)
            reg_names_parts.append(f"x{reg_num}")
        else:
            op_str_parts.append("")
            reg_names_parts.append("")

    instr_op_str = " , ".join(op_str_parts)
    print("instr_op_str", instr_op_str)
    reg_names_list = " , ".join(filter(None, reg_names_parts))
    print("reg_names_list", reg_names_list)

    # Handle immediate operand corner cases if present
    if has_imm_operand:
        print("has_imm_operand")
        print("imm_bit_len_list", imm_bit_len_list)
        num_imm = len(imm_bit_len_list)
        rows = num_imm * 3
        cols = len(operands)

        # Initialize matrices
        op_str_matrix = [["" for _ in range(cols)] for _ in range(rows)]
        instr_code_matrix = [0] * rows
        llvm_bytes_str_matrix = [""] * rows
        llvm_bytes_simple_str_matrix = [""] * rows

        # Split operand strings for filling matrix
        op_str_split = instr_op_str.split(" , ")
        imm_bit_len_split = imm_bit_len_list
        imm_bit_startpos_split = imm_bit_startpos_list

        imm_cnt = 0
        prev_imm_pos = -1

        for i in range(rows):
            imm_handled_in_row = False
            for j in range(cols):
                # Fill op_str_matrix with operand strings
                op_str_matrix[i][j] = op_str_split[j]

                # On every third row, replace immediate operands with corner cases
                if (
                    i > 0
                    and (i + 1) % 3 == 0
                    and op_str_split[j].isnumeric()
                    and not imm_handled_in_row
                    and j != prev_imm_pos
                ):
                    imm_bit_len = int(imm_bit_len_split[imm_cnt])
                    imm_bit_startpos = int(imm_bit_startpos_split[imm_cnt])
                    imm_range_limit = 1 << imm_bit_len

                    # Replace immediate operand in the previous 3 rows with corner cases: 0, mid, max
                    op_str_matrix[i - 2][j] = "0"
                    op_str_matrix[i - 1][j] = str(imm_range_limit // 2)
                    op_str_matrix[i][j] = str(imm_range_limit - 1)

                    # Update instruction codes with corner case values
                    base_code = instr_code
                    instr_code_matrix[i - 2] = set_bits_in_32bit_val(base_code, 0, imm_bit_startpos, imm_bit_len)
                    instr_code_matrix[i - 1] = set_bits_in_32bit_val(
                        base_code, imm_range_limit // 2, imm_bit_startpos, imm_bit_len
                    )
                    instr_code_matrix[i] = set_bits_in_32bit_val(
                        base_code, imm_range_limit - 1, imm_bit_startpos, imm_bit_len
                    )

                    imm_cnt += 1
                    prev_imm_pos = j
                    imm_handled_in_row = True

        # Convert instruction codes to LLVM byte strings
        for z in range(rows):
            code_hex = hex(instr_code_matrix[z])
            _, llvm_bytes_str_matrix[z], llvm_bytes_simple_str_matrix[z] = riscv_to_llvm_bytes(code_hex)
            # print(op_str_matrix[z], instr_code_matrix[z], llvm_bytes_str_matrix[z], llvm_bytes_simple_str_matrix[z])

    else:
        # No immediate operand, just return single code and LLVM bytes
        enc_hex = hex(instr_code)
        llvm_bytes_hex, llvm_bytes_str, llvm_bytes_simple_str = riscv_to_llvm_bytes(enc_hex)
        instr_code_matrix = [instr_code]
        llvm_bytes_str_matrix = [llvm_bytes_str]
        llvm_bytes_simple_str_matrix = [llvm_bytes_simple_str]
        op_str_matrix = [[instr_op_str]]

    return (
        instr_op_str,
        reg_names_list,
        has_imm_operand,
        instr_code_matrix,
        llvm_bytes_str_matrix,
        llvm_bytes_simple_str_matrix,
        op_str_matrix,
    )


def process_encoding(enc):
    # print("get_encoding", enc)
    operands = {}

    for e in reversed(enc):
        if isinstance(e, arch.BitField):
            name = e.name
            if name in operands:
                op = operands[name]
                op.lower = min(e.range.lower, op.lower)
                op.upper = max(e.range.upper, op.upper)
            else:
                op = Operand(name, e.range.lower, e.range.upper)
            operands[name] = op
    fields = []
    start = 0

    for e in reversed(enc):
        if isinstance(e, arch.BitField):
            name = e.name
            assert name in operands
            op = operands[name]
            if op.length > e.range.length:
                if e.range.length == 1:
                    name = name + "{" + str(e.range.lower - op.lower) + "}"
                else:
                    name = name + "{" + str(e.range.upper - op.lower) + "-" + str(e.range.lower - op.lower) + "}"
            new = EncodingField(name, start, e.range.length)
            start += e.range.length

        elif isinstance(e, arch.BitVal):
            new = EncodingField(None, start, e.length, e.value)

            start += e.length

        else:
            assert False
        fields.insert(0, new)

    return operands.values(), fields


def write_builtin_ll_test(instr_name, mnemonic, output_path, set_name: str, start_time: str):
    builtin_ll_template = Template(filename=str(template_dir / "test-builtin-ll.mako"))
    logger.info("writing builtin-ll tests for %s", mnemonic)

    arch = set_name.lower()

    txt = builtin_ll_template.render(
        start_time=start_time,
        set_name=set_name,
        instr_name=instr_name,
        mnemonic=mnemonic,
        arch=arch,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-builtin.ll", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_builtin_c_test(mnemonic, xlen, output_path, set_name: str, start_time: str):
    builtin_c_template = Template(filename=str(template_dir / "test-builtin-c.mako"))

    logger.info("writing builtin-c-tests for %s", mnemonic)
    arch = set_name.lower()

    txt = builtin_c_template.render(start_time=start_time, set_name=set_name, xlen=xlen, mnemonic=mnemonic, arch=arch)

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-builtin.c", "w", encoding="utf-8") as f:
        f.write(txt)


def write_cg_ll_test(instr_name, mnemonic, xlen, output_path, set_name: str, start_time: str):
    cg_ll_template = Template(filename=str(template_dir / "test-cg-ll.mako"))

    logger.info("writing cg-ll-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = cg_ll_template.render(
        start_time=start_time,
        set_name=set_name,
        instr_name=instr_name,
        mnemonic=mnemonic,
        arch=arch,
        xlen=xlen,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-cg.ll", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_cg_c_test(instr_name, mnemonic, xlen, output_path, set_name: str, start_time: str):
    cg_c_template = Template(filename=str(template_dir / "test-cg-c.mako"))

    logger.info("writing cg-c-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = cg_c_template.render(
        start_time=start_time,
        set_name=set_name,
        instr_name=instr_name,
        mnemonic=mnemonic,
        arch=arch,
        xlen=xlen,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-cg.c", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_compress_s_test(instr_name, mnemonic, xlen, output_path, set_name: str, start_time: str):
    compress_s_template = Template(filename=str(template_dir / "test-compress-s.mako"))

    logger.info("writing compress-s-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = compress_s_template.render(
        start_time=start_time, set_name=set_name, instr_name=instr_name, mnemonic=mnemonic, arch=arch, xlen=xlen
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-compress.s", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_inline_asm_c_test(
    instr_name, mnemonic, xlen, enc, reg_names_list, output_path, set_name: str, start_time: str
):
    inline_asm_c_template = Template(filename=str(template_dir / "test-inline-asm-c.mako"))

    logger.info("writing inline-asm-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = inline_asm_c_template.render(
        start_time=start_time,
        set_name=set_name,
        arch=arch,
        mnemonic=mnemonic,
        instr_name=instr_name,
        enc=enc,
        reg_names_list=reg_names_list.replace(" ,", ","),
        xlen=xlen,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-inline-asm.c", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_intrin_ll_test(instr_name, mnemonic, xlen, output_path, set_name: str, start_time: str):
    intrin_ll_template = Template(filename=str(template_dir / "test-intrin-ll.mako"))

    logger.info("writing intrin-ll-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = intrin_ll_template.render(
        start_time=start_time,
        set_name=set_name,
        arch=arch,
        mnemonic=mnemonic,
        instr_name=instr_name,
        xlen=xlen,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-intrin.ll", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_invalid_s_test(
    mnemonic, xlen, output_path, operand_str, num_operands, has_imm_operand, set_name: str, start_time: str
):
    logger.info("writing invalid-s-tests for %s", mnemonic)
    matrix = generate_invalid_operand_str(num_operands, operand_str, has_imm_operand)

    if has_imm_operand:
        invalid_s_template = Template(filename=str(template_dir / "test-invalid-imm-s.mako"))
    else:
        invalid_s_template = Template(filename=str(template_dir / "test-invalid-s.mako"))

    arch = set_name.lower()

    txt = invalid_s_template.render(
        start_time=start_time, set_name=set_name, arch=arch, mnemonic=mnemonic, xlen=xlen, matrix=matrix
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-invalid.s", "w", encoding="utf-8") as f:
        f.write(txt)

    return txt


def write_machine_code_test(
    instr_name,
    mnemonic,
    xlen,
    instr_op_str,
    has_imm_operand,
    op_str_matrix,
    llvm_bytes_str_matrix,
    output_path,
    set_name,
    start_time,
):

    if has_imm_operand:
        machine_code_template = Template(filename=str(template_dir / "test-mc-imm-s.mako"))
        enc = llvm_bytes_str_matrix
        instr_op_str = op_str_matrix
    else:
        machine_code_template = Template(filename=str(template_dir / "test-mc-s.mako"))
        enc = llvm_bytes_str_matrix

    logger.info("writing mc-s-tests for %s", mnemonic)

    arch = set_name.lower()

    txt = machine_code_template.render(
        start_time=start_time,
        set_name=set_name,
        arch=arch,
        mnemonic=mnemonic,
        instr_op_str=instr_op_str,
        enc=enc,
        xlen=xlen,
    )

    temp = mnemonic.lower().replace(".", "-")
    with open(output_path / f"{temp}.test-mc.s", "w", encoding="utf-8") as f:
        f.write(txt)


def write_instr_testcase_files(
    set_name,
    instr_name,
    real_name,
    asm_str,
    ins_str,
    outs_str,
    enc,
    fields,
    code,
    size,
    output_path,
    details_str,
    attrs: Optional[dict] = None,
    constraints: Optional[list] = None,
    formats=False,
    compressed_pat=None,
):
    start_time = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime())

    attrs = attrs or {}
    constraints = constraints or []

    if not formats:
        raise NotImplementedError("Instruction format support not implemented.")

    operands, fields = process_encoding(enc)
    (
        instr_op_str,
        reg_names_list,
        has_imm_operand,
        instr_code_matrix,
        llvm_bytes_str_matrix,
        llvm_bytes_simple_str_matrix,
        op_str_matrix,
    ) = generate_operand_str(operands, fields, code)
    num_operands = len(operands)

    # Convert bool attrs to int if needed
    attrs = {k: (int(v) if isinstance(v, bool) else v) for k, v in attrs.items()}
    constraints_str = ", ".join(constraints)
    instr_name = instr_name.lower()

    logger.info(f"Writing test files for instruction {instr_name} in set {set_name}")

    xlen = size

    # Compose test case strings using placeholder functions
    testcasegen_str = ""
    # if compressed_pat:
    # write_compress_s_test(instr_name, real_name, size, output_path, set_name, start_time)

    # write_builtin_c_test(real_name, xlen, output_path, set_name, start_time)
    # write_cg_c_test(instr_name, real_name, xlen, output_path, set_name, start_time)
    # write_compress_s_test(instr_name, real_name, xlen, output_path, set_name, start_time)
    write_inline_asm_c_test(
        instr_name, real_name, xlen, llvm_bytes_simple_str_matrix[0], reg_names_list, output_path, set_name, start_time
    )
    write_invalid_s_test(
        real_name, xlen, output_path, instr_op_str, num_operands, has_imm_operand, set_name, start_time
    )
    write_machine_code_test(
        instr_name,
        real_name,
        xlen,
        instr_op_str,
        has_imm_operand,
        op_str_matrix,
        llvm_bytes_str_matrix,
        output_path,
        set_name,
        start_time,
    )


def gen_instr_testcase_files(instr_def, set_def, output_path):
    # print("set name", set_def.name)
    set_name = set_def.name
    # print("instr", instr)
    name = instr_def.name
    # operands = instr_def.operands
    size = instr_def.size
    # print("operands", operands)
    # reads = instr.llvm_reads
    # writes = instr.llvm_writes
    constraints = instr_def.llvm_constraints
    # print("reads", reads)
    # print("writes", writes)
    constraints = instr_def.llvm_constraints
    # print("constraints", constraints)
    # constraints_str = ", ".join(constraints)
    # attributes = instr.attributes
    # print("attributes", attributes)
    real_name = instr_def.mnemonic
    asm_str = instr_def.llvm_asm_str
    # print("asm_str", asm_str)
    ins_str = instr_def.llvm_ins_str
    # print("ins_str", ins_str)
    outs_str = instr_def.llvm_outs_str
    # print("outs_str", outs_str)
    details_str = ""
    fields = instr_def.fields
    # print("fields")
    encoding = instr_def.encoding
    # print("encoding")
    attrs = instr_def.llvm_attributes

    code = instr_def.code
    # constraints = instr_def.constraints
    # if len(constraints) > 0:
    #     raise NotImplementedError
    formats = True
    compressed_pat = instr_def.llvm_get_compressed_pat(set_def)
    output_path = output_path / set_name

    write_instr_testcase_files(
        set_name,
        name,
        real_name,
        asm_str,
        ins_str,
        outs_str,
        encoding,
        fields,
        code,
        size,
        output_path,
        details_str,
        attrs=attrs,
        constraints=constraints,
        formats=formats,
        compressed_pat=compressed_pat,
    )


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set")
    parser.add_argument("--formats", action="store_true", help="Also generate instruction formats")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    parser.add_argument("--intrinsic", "-i", type=str, default=None)
    parser.add_argument(
        "--no-add-intrinsics",
        dest="add_intrinsics",
        default=True,
        action="store_false",
        help="Suppress patterns for intrinsic functions",
    )
    parser.add_argument("--ignore-failing", action="store_true", help="Do not crash in case of errors.")
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    assert args.output is not None
    out_path = pathlib.Path(args.output)
    assert out_path.is_dir()

    model_obj = load_model(top_level, compat=args.compat)

    if args.intrinsic is not None:
        model_obj.settings = Seal5Settings.from_yaml_file(args.intrinsic)
    print("settings", model_obj.settings)

    metrics = {
        "n_sets": 0,
        "n_instructions": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_instructions": [],
        "failed_instructions": [],
        "success_instructions": [],
        "skipped_sets": [],
        "failed_sets": [],
        "success_sets": [],
    }
    # preprocess model
    # print("model", model)

    settings = model_obj.settings
    # print (settings)

    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if args.splitted:
        content = ""
        # errs = []
        for set_name, set_def in model_obj.sets.items():
            metrics["n_sets"] += 1
            arch = set_name.lower()
            artifacts[set_name] = []
            xlen = set_def.xlen
            assert xlen is not None
            assert is_power_of_two(xlen)
            assert xlen % 8 == 0
            includes = []
            set_dir = out_path / set_name
            set_dir.mkdir(exist_ok=True)

            ext_settings = set_def.settings
            pred = None
            if ext_settings is not None:
                pred = "Has" + ext_settings.get_predicate(name=set_name)
            # TODO: check for GPRC and require HasStdExtCOrZca?
            # TODO: check for GPR32Pair and require HasGPR32Pair
            # TODO: check for GPR32V2/GPR32V4 and require HasGPR32V
            for _, instr_def in set_def.instructions.items():
                metrics["n_instructions"] += 1
                try:
                    metrics["n_success"] += 1
                    metrics["success_instructions"].append(instr_def.name)
                    content = gen_instr_testcase_files(instr_def, set_def, out_path)
                except Exception as ex:
                    logger.exception(ex)
                    metrics["n_failed"] += 1
                    metrics["failed_instructions"].append(instr_def.name)

            if settings.intrinsics.intrinsics is not None:
                for intrinsic in settings.intrinsics.intrinsics:
                    if intrinsic.set_name is not None and intrinsic.set_name != set_name:
                        continue
                #   try:
                #       intrinsic.
                #        arch_ = ext_settings.get_arch(name=set_name)
                #        if llvm_version is not None and llvm_version.major < 19:
                #            patch_frags["target"].contents += build_target(arch=arch_, intrinsic=intrinsic)
                #        else:
                #            patch_frags["target"].contents += build_target_new(arch=arch_, intrinsic=intrinsic, xlen=xlen)
                #        patch_frags["attr"].contents += build_attr(arch=arch_, intrinsic=intrinsic)
                #        patch_frags["emit"].contents += build_emit(arch=arch_, intrinsic=intrinsic)
                #        metrics["n_success"] += 1
                #        metrics["success_instructions"].append(intrinsic.instr_name)
                #    except Exception as ex:
                #        logger.exception(ex)
                #        metrics["n_failed"] += 1
                #        metrics["failed_instructions"].append(intrinsic.instr_name)
                #        metrics["failed_intrinsics"].append(?)
            metrics["success_sets"].append(set_name)

    else:
        raise NotImplementedError
    if not args.ignore_failing:
        n_failed = metrics["n_failed"]
        if n_failed > 0:
            failed = metrics["failed_instructions"]
            failing_str = ", ".join(failed)
            logger.error("%s intructions failed: %s", n_failed, failing_str)
            raise RuntimeError("Abort due to errors")


if __name__ == "__main__":
    main()
