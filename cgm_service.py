"""
example usage of GDBG
"""

import logging
import os
import sys

from datetime import datetime, timezone
from gdbg import GDBG


logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_log = logging.getLogger(__name__)


def log(msg):
    _log.info(f"[ Main ] {msg}")


class CGM_Service:
    """CGM_Service class using GDBG"""

    def __init__(self, dexcom_provider, dexcom_dir, time_step):
        ## initialize dexcom
        self.dexcom_dir = dexcom_dir
        self.time_step = time_step

        self.dexcom = dexcom_provider(
            self.dexcom_dir, self.time_step, self.cgm_service_callback
        )

    def cgm_service_callback(self):
        """called when new data is retrieved"""
        log(f"new status: {self.dexcom.status}")
        log(f"last update was {self.calculate_last_update()}")

    def calculate_last_update(self):
        """calculates min/sec since last bg reading"""
        time_diff = datetime.now(timezone.utc) - self.dexcom.datetime
        total_seconds = time_diff.total_seconds()

        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        return f"{formatted_time} minutes ago"

    def start(self):
        """start app and ticker in dexcom handler that updates bg"""
        log("Starting CGM Service")
        log(f"\tDexcom Directory: {self.dexcom_dir}")
        log(f"\tTime-Step: {self.time_step}")

        self.dexcom.start()


if __name__ == "__main__":
    dexcom_dir = f"{os.path.expanduser('~')}/.dexcom/"

    try:
        app = CGM_Service(dexcom_dir=dexcom_dir, time_step=5)
        app.start()

    except KeyboardInterrupt:
        log(
            "Program exited...\n\n\t\t(✦⚈_⚈)~~~☞ later babe\n",
        )
        sys.exit(0)

    except Exception as error:
        _log.error("error running CGM Service", str(error))
        sys.exit(1)
