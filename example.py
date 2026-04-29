import logging
import os
import sys

from datetime import datetime, timezone
from gdbg import GDBG

# TODO:
# * error handling everywhere
# * debug logging and better logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


class CGM_Service:
    """CGM_Service class using GDBG"""

    def __init__(self, dexcom_dir, time_step):
        ## initialize dexcom
        self.dexcom = GDBG(dexcom_dir, time_step, self.cgm_service_callback)

        self.dexcom_dir = dexcom_dir
        self.time_step = time_step

    def cgm_service_callback(self):
        """called when new data is retrieved"""
        print(self.dexcom.reading)

    # def calculate_last_update(self):
    #     """calculates min/sec since last bg reading"""
    #     time_diff = datetime.now(timezone.utc) - self.dexcom.datetime
    #     total_seconds = time_diff.total_seconds()

    #     minutes = int(total_seconds // 60)
    #     seconds = int(total_seconds % 60)
    #     formatted_time = f"{minutes:02d}:{seconds:02d}"

    #     return f"{formatted_time} minutes ago"

    def start(self):
        """start app and ticker in dexcom handler that updates bg"""
        log.info("Starting CGM Service")
        log.info("  Dexcom Directory: " + self.dexcom)
        log.info("  Time-Step: " + self.time_step)

        self.dexcom.start()


if __name__ == "__main__":
    dexcom_dir = os.path.expanduser("~") + "/.dexcom/"

    try:
        app = CGM_Service(dexcom_dir=dexcom_dir, time_step=5)
        app.start()
    except Exception as error:
        log.error("error running app", str(error))
        sys.exit(1)
