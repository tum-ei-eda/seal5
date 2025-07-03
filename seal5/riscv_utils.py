from typing import Optional, List, Tuple
from seal5.settings import RISCVSettings
import re
import time



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

def set_bits_in_32bit_val(original: int, value: int, position: int, bit_length: int) -> int:
    """
    Insert 'bit_length' bits from 'value' into 'original' starting at 'position'.
    Bits are zero-indexed from the right (LSB=0).
    """
    if not (0 <= value < 2 ** bit_length):
        raise ValueError(f"value must fit in {bit_length} bits (0 to {2 ** bit_length - 1})")
    if not (0 <= position <= 32 - bit_length):
        raise ValueError(f"position must be between 0 and {32 - bit_length}")

    mask = (1 << bit_length) - 1
    original_cleared = original & ~(mask << position)
    value_masked_shifted = (value & mask) << position
    modified = original_cleared | value_masked_shifted
    return modified & 0xFFFFFFFF  # Ensure 32-bit

def riscv_to_llvm_bytes(hex_value: str) -> Tuple[List[str], str, str]:
    """
    Convert 32-bit hex instruction to little-endian LLVM byte strings.
    Returns (list_of_hex_bytes, joined_hex_string, simple_joined_string).
    """
    hex_str = hex_value.lower().replace('0x', '').zfill(8)
    bytes_list = [hex_str[i:i+2] for i in range(0, 8, 2)]
    llvm_bytes = list(reversed(bytes_list))

    llvm_bytes_hex = [f"0x{b}" for b in llvm_bytes]
    llvm_bytes_str = ", ".join(llvm_bytes_hex)
    llvm_bytes_simple_str = ", ".join(llvm_bytes)

    return llvm_bytes_hex, llvm_bytes_str, llvm_bytes_simple_str

def replace_imm_whole_word_case_insensitive(input_str: str) -> str:
    """
    Replace whole-word 'imm' (case-insensitive) with random integer 0-31.
    """
    pattern = re.compile(r"\bimm\b", re.I)
    return pattern.sub(lambda _: str(random.randint(0, 31)), input_str)

def get_abi_name(reg_name: str) -> str:
    """
    Convert RISC-V register name to ABI name, e.g. x10 -> a0.
    Extend mapping as needed.
    """
    abi_map = {
        'x0':  'zero', 'x1': 'ra', 'x2': 'sp', 'x3': 'gp',
        'x4':  'tp', 'x5':  't0', 'x6':  't1', 'x7':  't2',
        'x8':  's0',  # or fp (frame pointer),
        'x9':  's1',
        'x10': 'a0', 'x11': 'a1', 'x12': 'a2', 'x13': 'a3',
        'x14': 'a4', 'x15': 'a5', 'x16': 'a6', 'x17': 'a7',
        'x18': 's2', 'x19': 's3', 'x20': 's4', 'x21': 's5',
        'x22': 's6', 'x23': 's7', 'x24': 's8', 'x25': 's9',
        'x26': 's10', 'x27': 's11', 'x28': 't3', 'x29': 't4',
        'x30': 't5','x31': 't6'
    }
    return abi_map.get(reg_name, reg_name)
