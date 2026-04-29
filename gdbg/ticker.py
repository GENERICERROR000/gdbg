import logging
import time

from datetime import datetime, timedelta, timezone

# TODO:
# * HERE (still issue?)
#   * this is where to check for stale data and handle refresh
#   * need a way to have bg data shown as stale
# * new thing though:
#   * try to grab
#   * if good, see you in 5:20
#   * if not, retry 15 seconds later
#   * if not, retry 30 seconds later
#   * if not, retry 60 seconds later
#   * if not, go back to every 5 min (need to preserve previous time then)
#   * (is this where to flip switch saying stale?)
#   *

_log = logging.getLogger(__name__)


def log(msg):
    _log.info("Ticker | " + msg)


class Ticker:
    """
    class to create a timer that executes `callback` every `interval`

    * `ticker_exec`: can be used on it's own with an external timer
    * `datetime`: must be set in the `internal_callback` or `callback`
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

            ## HERE:
            self.internal_callback()

            if self.callback:
                self.callback()

            timestamp = self.datetime
            # add 5:20 min
            future_datetime = timestamp + timedelta(seconds=320)
            interval = (future_datetime - datetime.now(timezone.utc)).seconds

            # HERE: old spot, if use new one, then time stuff happens before moving on to callback...

            # if time has passed, try again every 15s
            self.interval = max(15, interval)
            self.count = 0
            self.updating = False

    def start(self):
        """start the ticker loop"""
        log(f"Starting loop with time_step of: {self.time_step} seconds")
        while True:
            time.sleep(self.time_step)
            self.ticker_exec()
