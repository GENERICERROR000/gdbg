import logging
import threading

# import time

from datetime import datetime, timedelta, timezone


_log = logging.getLogger(__name__)


def log(msg):
    _log.info(f"[ Ticker ] {msg}")


def debug(msg):
    _log.debug(f"[ Ticker ] {msg}")


class Ticker:
    """
    class to create a timer that executes `callback` every `interval`

    * `ticker_exec`: can be used on it's own with an external timer
    * WARN: `datetime`: must be set/updated by `internal_callback` or `callback`
        * used for calculating time passed and retries after 15 minutes
    """

    def __init__(self, time_step, internal_callback, callback):
        """
        * `time_step`: how often the Ticker runs a loops (in seconds)
        * `internal_callback`: fn executed every loop
            * set by whatever is initializing the Ticker
            * something like checking an API end point for data
        * `callback`: fn executed every loop
            * set by whatever is initializing something that has already created a Ticker
            * something like updating a gui based on data retrieved from an API
        """
        self.time_step = time_step
        self.callback = callback
        self.internal_callback = internal_callback

        self.interval = 0
        self.count = 0
        self.updating = False
        self.is_reading_stale = False
        self.backoff = 15
        self.skip_backoff = False

        self.datetime = None

    def set_datetime(self, datetime):
        """
        set datetime

        if reading is the same as the previous one, update time stamp to previous + 5 minutes
        """
        if self.datetime == datetime:
            self.datetime = datetime.now(timezone.utc)

        else:
            self.datetime = datetime

    ## second arg is in case using an outside timer that passes arg
    def ticker_exec(self, _=None):
        """
        fn that checks every `time_step` (seconds) if interval has been reached.

        if passed interval, get new reading for dexcom and use callback if set.
        """
        self.count += self.time_step

        debug(f"\t\t\t\t\t{self.count} (count) | {self.interval} (interval)")

        if self.count >= self.interval and not self.updating:
            self.updating = True

            debug(f"{self.count} (count) >= {self.interval} (interval)")

            if self.internal_callback:
                log("internal_callback")
                self.is_reading_stale = self.internal_callback()

            if self.callback:
                log("callback")
                self.callback()

            if self.is_reading_stale:
                backoff_seconds = None

                if self.skip_backoff:
                    log("Skipping retries, checking every 5 minutes")
                    # backoff_seconds = datetime.now(timezone.utc) + timedelta(
                    #     seconds=300
                    # )
                    backoff_seconds = 300

                else:
                    log(f"retrying in approximately {self.backoff} seconds...")
                    # backoff_seconds = datetime.now(timezone.utc) + timedelta(
                    #     seconds=self.backoff
                    # )
                    backoff_seconds = self.backoff

                    self.backoff *= 2

                    if self.backoff > 60:
                        debug("setting skip_backoff = True (tried 3 times)")
                        self.skip_backoff = True
                        self.backoff = 15

                self.interval = backoff_seconds
                debug(f"new interval:  {self.interval} (seconds)")

            else:
                timestamp = self.datetime

                ## add 5:20 min
                future_datetime = timestamp + timedelta(seconds=320)
                interval = (future_datetime - datetime.now(timezone.utc)).seconds

                ## set interval to minimum of 60 seconds
                self.interval = max(60, interval)
                debug(f"new interval:  {self.interval} (seconds)")

                ## reset check
                if self.skip_backoff:
                    self.skip_backoff = False
                    debug(f"reset skip_backoff: {self.skip_backoff}")

            self.count = 0
            self.updating = False

    def start(self):
        """start the ticker loop"""
        event = threading.Event()

        log(f"Starting loop with time_step of: {self.time_step} seconds")

        while True:
            event.wait(self.time_step)
            # time.sleep(self.time_step)
            self.ticker_exec()
