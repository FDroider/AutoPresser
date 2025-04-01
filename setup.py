from cx_Freeze import setup, Executable
build_options={
    "optimize": 2,
    "include_files": ["images"],
    "includes": ["pynput.keyboard._xorg", "pynput.mouse._xorg"],
    "packages": ["Xlib"]
}

setup(
    name="AutoPresser",
    version="1.7.0",
    description="Auto presser and clicker in one app",
    author="FDroider",
    keywords=["Clicker", "Presser", "AutoPresser", "AutoClicker"],
    options={"build_exe": build_options,
             "bdist_appimage": {},
             "bdist_rpm": {"vendor": "FDroider",
                           "provides": "Auto-cliker/presser mouse button or keyboard button"}},
    executables=[{"script": "main.py", "base": "gui", "target_name": "AutoPresser", "icon": "autopresser_icon.svg"}]
)