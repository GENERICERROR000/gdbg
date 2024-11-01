import os
import json
import rumps
from datetime import datetime, timedelta, timezone
from dexcom_api import DexcomAPI


class GDBG(rumps.App):
    def __init__(self, dexcom_dir):
        super().__init__("gdbg")

        self.dexcom_dir = dexcom_dir
        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"

        # run timer every 10 seconds instead of every second
        self.time_step = 10
        self.count = 0
        self.interval = 0
        self.timer = rumps.Timer(self.begin_refreshing, self.time_step)

        self.set_up_menu()
        self.setup_dexcom()
        self.timer.start()

    def setup_dexcom(self):
        self.dexcom = DexcomAPI(self.dexcom_dir)
        print("setup_dexcom")

    def begin_refreshing(self, _):

        # HERE:
        # TODO: timer logic isnt quite right, it kept calling too much

        self.count += self.time_step

        if self.count > self.interval:
            self.timer.stop()
            self.get_dexcom_reading(None)

            timestamp = self.dexcom.reading.datetime
            future_datetime = timestamp + timedelta(seconds=310)  # Add 5:10 min
            interval = (future_datetime - datetime.now(timezone.utc)).seconds

            self.interval = interval
            print(interval)
            self.count = 0
            self.timer.start()

    def get_dexcom_reading(self, _):
        self.dexcom.get_reading()
        self.update_status()
        self.write_state()

    def update_status(self):
        self.title = self.dexcom.status

    def write_state(self):
        with open(self.state_file, "w") as f:
            f.write(self.dexcom.status)

        with open(self.state_color_file, "w") as f:
            f.write(self.dexcom.color_status)

    def set_up_menu(self):
        self.title = "--"
        self.menu = [
            "last checked",
            "change: +/-",
            rumps.separator,
            "[ ] alert on low",
            rumps.MenuItem(title="Refresh", callback=self.get_dexcom_reading),
            rumps.separator,
        ]


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    app = GDBG(dexcom_dir)
    app.run()
