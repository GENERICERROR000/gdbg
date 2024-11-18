import logging
import os
import rumps
import sys
from datetime import datetime, timezone
from gdbg import GDBG


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


class MacOSStatusbar(object):
    """class to create rumps app and using dexcom handler"""

    def __init__(self, dexcom_dir, time_step):
        self.app = rumps.App("gdbg")

        self.setup_menu()
        self.setup_dexcom(dexcom_dir, time_step)

        # use rumps ticker instead of GDBG's to avoid issues when computer sleeps
        self.ticker = rumps.Timer(self.dexcom.ticker.ticker_exec, time_step)
        self.update_timer = rumps.Timer(self.update_time_callback, 1)

    def update_time_callback(self, _):
        """callback used by app timer to update time since last reading in app menu"""
        if self.dexcom.datetime:
            # menu_items = self.app.menu.items()
            # menu_items[1][1].title = self.calculate_last_update()
            self.app.menu = [
                self.dexcom.delta,
                self.calculate_last_update(),
                rumps.separator,
                rumps.MenuItem(title="Refresh", callback=self.refresh_callback),
                rumps.separator,
            ]

    def refresh_callback(self, _):
        """callback used by Refresh button in app menu to get new reading and update app menu"""
        self.dexcom.get_reading()
        self.update_menu()

    def ticker_callback(self):
        """callback used by dexcom ticker ever `time_step` to update app menu"""
        self.update_menu()

    def setup_menu(self):
        """setup rumps app menu"""
        self.app.title = "--"
        self.app.menu = [
            "delta",
            "last update",
            rumps.separator,
            rumps.MenuItem(title="Refresh", callback=self.refresh_callback),
            rumps.separator,
        ]

    def setup_dexcom(self, dexcom_dir, time_step):
        """initialize dexcom"""
        self.dexcom = GDBG(dexcom_dir, time_step)
        self.dexcom.set_callback(self.ticker_callback)

    def calculate_last_update(self):
        """calculates min/sec since last bg reading"""
        time_diff = datetime.now(timezone.utc) - self.dexcom.datetime
        total_seconds = time_diff.total_seconds()

        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        return f"{formatted_time} minutes ago"

    # NOTE: updates menu in-place to avoid memory leak
    # (https://github.com/jaredks/rumps/issues/216#issuecomment-2329613243)
    def update_menu(self):
        """update title with new bg and update delta in menu"""
        self.app.title = self.dexcom.short_status

        menu_items = self.app.menu.items()
        menu_items[0][1].title = self.dexcom.delta

    def begin_refresh_ticker(self):
        """start ticker in dexcom handler that updates bg"""
        self.dexcom.start()

    def start(self):
        """start rumps app"""
        log.info("starting app: " + self.app.name)

        self.ticker.start()
        self.update_timer.start()
        self.app.run()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    try:
        app = MacOSStatusbar(dexcom_dir=dexcom_dir, time_step=5)
        app.start()
    except Exception as error:
        log.error("error running app", str(error))
        sys.exit(1)
