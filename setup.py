from setuptools import setup

APP = ["gdbg/gdbg.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "assets/gdbg_logo.icns",
    "plist": {
        "CFBundleShortVersionString": "0.1.0",
        "LSUIElement": True,
    },
    "frameworks": ["/opt/homebrew/opt/libffi/lib/libffi.8.dylib"],
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
