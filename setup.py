from cx_Freeze import setup, Executable
import sys

#build_exe_options = {"packages": ["random"]}

setup(
      name="game.exe",
      version="1.0",
      author="Sam Von Ehren",
      description="Copyright 2013",
#      options = {"build_exe":build_exe_options},
      executables=[Executable("main.py", base = "Win32GUI")]
      )
