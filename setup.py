import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": [],
                     "excludes": ["matplotlib.tests", "numpy.random._examples"],
                     "include_files": ["icons/"],
                     # "include_files": ["clipboard.png", "coffee.png", "folder.png", "group.png", "iv_off.png",
                     #                   "iv_on.png", "lambda.png", "minus.png", "move_down.png", "move_up.png",
                     #                   "plus.png", "power_off.png", "power_on.png", "refresh.png", "save.png",
                     #                   "select_all.png", "select_none.png", "temp_off.png", "temp_on.png"],
                     "includes": "atexit"}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="ItMakesCoffee",
      version="2020.7.29",
      description="Lambda IV Measurement and Analysis Software",
      options={"build_exe": build_exe_options},
      executables=[Executable("itmakescoffee.py", base=base)])
