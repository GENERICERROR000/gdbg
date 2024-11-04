import os
import rumps
from datetime import datetime, timezone
from dexcom_handler import DexcomHandler
from threading import Thread


class GDBG(object):
    def __init__(self, dexcom_dir, time_step):
        self.app = rumps.App("gdbg")
        self.setup_menu()
        self.setup_dexcom(dexcom_dir, time_step)

    def setup_menu(self):
        self.app.title = "--"
        self.app.menu = [
            "delta",
            "last update",
            rumps.separator,
            rumps.MenuItem(title="Refresh", callback=self.menu_callback),
            rumps.separator,
        ]

    def setup_dexcom(self, dexcom_dir, time_step):
        self.dexcom = DexcomHandler(dexcom_dir, time_step)
        self.dexcom.set_callback(self.ticker_callback)

    def begin_refresh_ticker(self):
        self.dexcom.run()

    def menu_callback(self, _):
        self.get_dexcom_reading()

    def ticker_callback(self):
        self.get_dexcom_reading()

    def get_dexcom_reading(self):
        self.dexcom.get_reading()
        self.update_menu()

    def quit_app(self, _):
        rumps.quit_application()

    # TODO: this needs to update every x amount of time
    # (currently only called when dexcom bg updates... may need another ticker)
    # (https://camillovisini.com/coding/create-macos-menu-bar-app-pomodoro)
    def calculate_last_update(self):
        time_diff = datetime.now(timezone.utc) - self.dexcom.datetime
        minutes_passed = time_diff.total_seconds() / 60

        return f"{minutes_passed:.2f} minutes ago"

    def calculate_delta(self):
        delta = str(self.dexcom.bg_value - self.dexcom.previous_bg_value)
        if int(delta) > 0:
            delta = "+" + delta

        return delta

    def update_menu(self):
        self.app.title = self.dexcom.status

        delta = self.calculate_delta()
        last_update = self.calculate_last_update()
        new_menu = [
            delta,
            last_update,
            rumps.separator,
            rumps.MenuItem(title="Refresh", callback=self.menu_callback),
            rumps.separator,
            rumps.MenuItem(title="Quit", callback=self.quit_app),
        ]

        self.app.menu.clear()
        self.app.menu.update(new_menu)

    def start(self):
        self.app.run()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    app = GDBG(dexcom_dir=dexcom_dir, time_step=5)
    ticker_thread = Thread(target=app.begin_refresh_ticker, daemon=True)

    ticker_thread.start()
    app.start()
