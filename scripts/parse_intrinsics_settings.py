import sys
from seal5.settings import Seal5Settings

assert len(sys.argv) == 2

settings_file = sys.argv[1]

settings = Seal5Settings.from_yaml_file(settings_file)
print("settings", settings)
