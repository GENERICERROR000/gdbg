import os
import rumps
from datetime import datetime, timezone
from dexcom_handler import DexcomHandler
from threading import Thread


class GDBG(object):
    def __init__(self, dexcom_dir, time_step):
        self.app = rumps.App("gdbg")
        self.update_timer = rumps.Timer(self.update_time_callback, 1)

        self.setup_menu()
        self.setup_dexcom(dexcom_dir, time_step)

    def update_time_callback(self, _):
        """TODO: add fn comments to all fn's"""
        if self.dexcom.datetime:
            menu_items = self.app.menu.items()
            menu_items[1][1].title = self.calculate_last_update()
    
    def refresh_callback(self, _):
        self.get_dexcom_reading()

    def ticker_callback(self):
        self.get_dexcom_reading()

    def setup_menu(self):
        self.app.title = "--"
        self.app.menu = [
            "delta",
            "last update",
            rumps.separator,
            rumps.MenuItem(title="Refresh", callback=self.refresh_callback),
            rumps.separator,
        ]

    def setup_dexcom(self, dexcom_dir, time_step):
        self.dexcom = DexcomHandler(dexcom_dir, time_step)
        self.dexcom.set_callback(self.ticker_callback)

    def get_dexcom_reading(self):
        self.dexcom.get_reading()
        self.update_menu()

    # TODO: move to dexcom_handler
    def calculate_last_update(self):
        time_diff = datetime.now(timezone.utc) - self.dexcom.datetime
        total_seconds = time_diff.total_seconds()

        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        return f"{formatted_time} minutes ago"

    # TODO: move to dexcom_handler
    def calculate_delta(self):
        delta = str(self.dexcom.bg_value - self.dexcom.previous_bg_value)
        if int(delta) > 0:
            delta = f"+{delta}"

        return delta

    # NOTE: updates menu in-place to avoid memory leak
    # (https://github.com/jaredks/rumps/issues/216#issuecomment-2329613243)
    def update_menu(self):
        self.app.title = self.dexcom.status

        menu_items = self.app.menu.items()
        menu_items[0][1].title = self.calculate_delta()

    def begin_refresh_ticker(self):
        self.dexcom.run()

    def start(self):
        self.update_timer.start()
        self.app.run()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    app = GDBG(dexcom_dir=dexcom_dir, time_step=5)
    ticker_thread = Thread(target=app.begin_refresh_ticker, daemon=True)

    ticker_thread.start()
    app.start()
