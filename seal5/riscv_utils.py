from typing import Optional

from seal5.settings import RISCVSettings


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
