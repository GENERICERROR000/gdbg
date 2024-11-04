from setuptools import setup

APP = ["gdbg.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "assets/gdbg_logo.icns",
    "plist": {
        "CFBundleShortVersionString": "0.0.1",
        "LSUIElement": True,
    },
    "packages": ["imp", "pydexcom", "rumps"],
    # https://github.com/jawah/charset_normalizer/issues/253#issuecomment-1821092802
    "includes": ["charset_normalizer.md__mypyc"],
}

setup(
    name="gdbg",
    description="get dexcom blood glucose",
    author="GENERIC_ERROR",
    python_requires="==3.12",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=["rumps"],
)
