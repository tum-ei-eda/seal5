import re

from seal5.settings import Seal5Settings, PatchSettings, DEFAULT_SETTINGS, LLVMConfig, LLVMVersion


def parse_cond(cond, settings: Seal5Settings):
    res = eval(cond, {"__builtins__": {}}, {"settings": settings})
    return res


# settings = Seal5Settings.from_dict(DEFAULT_SETTINGS)
settings = Seal5Settings.from_yaml_file("/tmp/seal5_llvm_corev_llvm19/.seal5/settings.yml")
print("settings", settings)

# cond = "settings.llvm.state.version.major == 19"
cond = "print(dir())"

res = parse_cond(cond, settings)

print("res", res)
