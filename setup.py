from cx_Freeze import setup, Executable
from os import listdir
build_options={
    "optimize": 2,
    "include_files": [f"./Images/{i}" for i in listdir("./Images")],
    "includes": ["pynput.keyboard._xorg", "pynput.mouse._xorg"],
    "packages": ["Xlib"]
}

setup(
    name="AutoPresser",
    version="1.6.2",
    description="AutoPresser",
    author="FDroider",
    keywords=["Clicker", "Presser", "AutoPresser", "AutoClicker"],
    options={"build_exe": build_options},
    executables=[Executable("main.py")]
)