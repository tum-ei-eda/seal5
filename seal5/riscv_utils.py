from typing import Optional

from seal5.settings import RISCVSettings
from seal5.model import Seal5OperandAttribute

from m2isar.metamodel import arch


def get_riscv_defaults(riscv_settings: Optional[RISCVSettings] = None):
    default_features = ["+m", "+fast-unaligned-access"]
    default_xlen = None
    if riscv_settings:
        default_features_ = riscv_settings.features
        if default_features_ is not None:
            default_features = default_features_
        default_xlen_ = riscv_settings.xlen
        if default_xlen is not None:
            default_xlen = default_xlen_
    return default_features, default_xlen


def build_riscv_mattr(features, xlen: Optional[int] = None):
    mattrs = []

    def fix_prefix(x):
        assert len(x) > 0
        if x[0] in ["-", "+"]:
            return x
        return f"+{x}"

    if features is not None:
        mattrs += list(features)
    if xlen is not None:
        if xlen == 64:
            mattrs += ["64bit"]
    mattrs = list(set(map(fix_prefix, mattrs)))
    mattr = ",".join(mattrs)
    return mattr


def detect_opcode(instr_def):  # TODO: move to transform and store as attr
    OPCODE_LOOKUP = {
        "LOAD": 0b00000,
        "LOAD-FP": 0b00001,
        "custom-0": 0b00010,
        "MISC-MEM": 0b00011,
        "OP-IMM": 0b00100,
        "AUIPC": 0b00101,
        "OP-IMM-32": 0b00110,
        # "48bit": 0b00111,
        "STORE": 0b01000,
        "STORE-FP": 0b01001,
        "custom-1": 0b01010,
        "AMO": 0b01011,
        "OP": 0b01100,
        "LUI": 0b01101,
        "OP-32": 0b01110,
        # "64bit": 0b01111,
        "MADD": 0b10000,
        "MSUB": 0b10001,
        "NMADD": 0b10010,
        "NMSUB": 0b10011,
        "OP-FP": 0b10100,
        "OP-V": 0b10101,
        "custom-2": 0b10110,  # rv128i
        # "48bit2": 0b10111,
        "BRANCH": 0b11000,
        "JALR": 0b11001,
        # "reserved": 0b11010,
        "JAL": 0b11011,
        "SYSTEM": 0b11100,
        "OP-P": 0b11101,
        "custom-3": 0b11110,
        # "80bit+": 0b11111,
    }
    OPCODE_LOOKUP_REV = {v: k for k, v in OPCODE_LOOKUP.items()}
    size = 0  # TODO: use instr_def.size
    opcode = None
    for e in reversed(instr_def.encoding):
        # print("e", e, dir(e))
        if isinstance(e, arch.BitVal):
            length = e.length
            if size == 0:
                val = e.value
                if length >= 7:
                    val = val & 0b1111111
                    opcode = val >> 2
        elif isinstance(e, arch.BitField):
            length = e.range.length
        else:
            assert False
        size += length
    if size != 32:  # TODO: support compressed opcodes
        assert size == 16
        return "COMPRESSED", opcode
    assert opcode is not None
    found = OPCODE_LOOKUP_REV.get(opcode, None)
    assert found is not None, f"Opcode not found: {bin(opcode)}"
    return found, opcode


def detect_funct3_funct7(instr_def):
    size = 0  # TODO: use instr_def.size
    funct3 = None
    funct7 = None
    if size != 32:  # TODO: support compressed opcodes
        return None, None
    for e in reversed(instr_def.encoding):
        # print("e", e, dir(e))
        if isinstance(e, arch.BitVal):
            length = e.length
            if size == 7 + 5:
                val = e.value
                if length == 3:
                    funct3 = val
            elif size == 7 + 5 + 3 + 5 + 5:
                val = e.value
                if length == 7:
                    funct7 = val
        elif isinstance(e, arch.BitField):
            length = e.range.length
        else:
            assert False
        size += length
        assert size == 16
        return "COMPRESSED"
    return funct3, funct7


def detect_format(instr_def):  # TODO: move to transform and store as attr
    # enc = instr_def.encoding
    operands = instr_def.operands
    char_lookup = {}
    imm_char = "a"
    reg_char = "A"
    temp = ""
    for e in reversed(instr_def.encoding):
        if isinstance(e, arch.BitVal):
            new = bin(e.value)[2:].zfill(e.length)
            temp = f"{new}{temp}"
        elif isinstance(e, arch.BitField):
            length = e.range.length
            found = char_lookup.get(e.name, None)
            char = "#"
            if found is not None:
                char = found
            else:
                op = operands.get(e.name, None)
                if op is not None:
                    if Seal5OperandAttribute.IS_REG in op.attributes:
                        char = reg_char
                        reg_char = chr(ord(reg_char) + 1)
                    elif Seal5OperandAttribute.IS_IMM in op.attributes:
                        char = imm_char
                        imm_char = chr(ord(imm_char) + 1)
                    else:
                        char = "%"
                char_lookup[e.name] = char
            new = char * length
            temp = f"{new}{temp}"
        else:
            assert False
    FMT_LOOKUP = [  # needs to be sorted by weight (number of non-?)
        ("aaaaaaaBBBBBAAAAA???aaaaa???????", "s-type (mem)"),
        ("??aaaaaCCCCCBBBBB???AAAAA???????", "f2-type (binop)"),
        ("??bbbbbaaaaaBBBBB???AAAAA???????", "f2-type (unop)"),
        ("???????CCCCCBBBBB???AAAAA???????", "r-type (binop)"),
        ("???????BBBBBAAAAA???00000???????", "r-type (binop, noout)"),
        ("???????00000BBBBB???AAAAA???????", "r-type (unop)"),
        ("???????00000BBBBB???00000???????", "r-type (unop, noout)"),
        ("???????0000000000???AAAAA???????", "r-type (nonop)"),
        ("???????0000000000???00000???????", "r-type (nonop)"),  # s4emac
        ("???????aaaaaBBBBB???AAAAA???????", "ri-type (binop)"),
    ]
    found2 = f"unknown[{temp}]"
    for mask, fmt in FMT_LOOKUP:
        if len(mask) != len(temp):
            continue
        masked = "".join([c if mask[i] != "?" else "?" for i, c in enumerate(temp)])
        if masked == mask:
            found2 = fmt
            break
    return found2, temp
