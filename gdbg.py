import os
import rumps
from dexcom_handler import DexcomHandler
from threading import Thread


class GDBG(object):
    def __init__(self, dexcom_dir, time_step):
        self.app = rumps.App("gdbg")
        self.setup_menu()
        self.setup_dexcom(dexcom_dir, time_step)

    def setup_dexcom(self, dexcom_dir, time_step):
        self.dexcom = DexcomHandler(dexcom_dir, time_step)
        self.dexcom.set_callback(self.get_dexcom_reading_callback)

    def begin_refresh_ticker(self):
        self.dexcom.run()

    def get_dexcom_reading(self):
        self.dexcom.get_reading()
        self.update_status()

    def get_dexcom_reading_callback(self, _):
        self.dexcom.get_reading()
        self.update_status()

    def update_status(self):
        self.app.title = self.dexcom.status

    def setup_menu(self):
        self.app.title = "--"
        self.app.menu = [
            "last checked",
            "change: +/-",
            rumps.separator,
            "[ ] alert on low",
            rumps.MenuItem(title="Refresh", callback=self.get_dexcom_reading),
            rumps.separator,
        ]

    def start(self):
        self.app.run()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    app = GDBG(dexcom_dir=dexcom_dir, time_step=5)
    ticker_thread = Thread(target=app.begin_refresh_ticker, daemon=True)

    ticker_thread.start()
    app.start()
