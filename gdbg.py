import os
import json
import rumps
from dexcom_api import DexcomAPI


class Timer:
    def __init__(self):
        self.a = ""


class GDBG(object):
    def __init__(self, dexcom_dir):
        self.app_name = "gdbg"
        self.dexcom_dir = dexcom_dir
        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"

        self.app = rumps.App(self.app_name)
        self.setup_dexcom_and_begin_refresihing()
        self.set_up_menu()

    def set_up_menu(self):
        self.app.title = self.app_name

        self.app.menu = [
            "last checked",
            "change: +/-",
            rumps.separator,
            "[ ] alert on low",
            rumps.MenuItem(title="Refresh", callback=self.get_dexcom_reading),
            rumps.separator,
        ]

    def update_status(self):
        self.app.title = self.dexcom.status

    def write_state(self):
        dexcom = self.dexcom

        with open(self.state_file, "w") as f:
            f.write(dexcom.status)

        with open(self.state_color_file, "w") as f:
            f.write(dexcom.color_status)

    def get_dexcom_reading(self, _):
        self.dexcom.get_reading()
        self.update_status()
        self.write_state()

    def setup_dexcom_and_begin_refresihing(self):
        self.dexcom = DexcomAPI(self.dexcom_dir)
        # TODO: intit timer and it calls this
        self.get_dexcom_reading()

    def run(self):
        self.app.run()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    app = GDBG(dexcom_dir)
    app.run()
