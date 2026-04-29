import logging
import time

from datetime import datetime, timedelta, timezone


_log = logging.getLogger(__name__)


def log(msg):
    _log.info("Ticker | " + msg)


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
        """
        self.datetime = datetime

    ## second arg is in case using an outside timer that passes arg
    def ticker_exec(self, _=None):
        """
        fn that checks every `time_step` (seconds) if interval has been reached.

        if passed interval, get new reading for dexcom and use callback if set.
        """
        self.count += self.time_step

        if self.count >= self.interval and not self.updating:
            self.updating = True

            log(f"{self.count} (count) >= {self.interval} (interval)")

            if self.internal_callback:
                log("internal_callback")
                self.internal_callback()

            if self.callback:
                log("callback")
                self.is_reading_stale = self.callback()

            # if self.is_reading_stale and not self.skip_backoff:
            if self.is_reading_stale:
                if self.skip_backoff:
                    log("Skipping retries, check every 5 minutes")
                    future_datetime = datetime.now(timezone.utc) + timedelta(
                        seconds=300
                    )
                else:
                    log(f"retrying in approximately {self.backoff} seconds...")
                    future_datetime = datetime.now(timezone.utc) + timedelta(
                        seconds=self.backoff
                    )

                    self.backoff *= 2

                    if self.backoff > 60:
                        log(
                            "Retried 3 times, skipping backoff and retrying ever 5 minutes"
                        )
                        self.skip_backoff = True
                        self.backoff = 15

            else:
                timestamp = self.datetime

                ## add 5:20 min
                future_datetime = timestamp + timedelta(seconds=320)
                interval = (future_datetime - datetime.now(timezone.utc)).seconds

                ## set interval to minimum of 60 seconds
                self.interval = max(60, interval)

                ## reset check
                if self.skip_backoff:
                    self.skip_backoff = False

            self.count = 0
            self.updating = False

    def start(self):
        """start the ticker loop"""
        log(f"Starting loop with time_step of: {self.time_step} seconds")

        while True:
            time.sleep(self.time_step)
            self.ticker_exec()
