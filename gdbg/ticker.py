import time
from datetime import datetime, timedelta, timezone


class Ticker:
    """
    class to create a timer that executes fn every `interval`

    `ticker_exec` can be used on it's own with an external timer
    """

    def __init__(self, get_reading_callback, time_step):
        self.get_reading = get_reading_callback
        self.time_step = time_step
        self.interval = 0
        self.count = 0
        self.updating = False
        self.delta = None
        self.datetime = None
        self.callback = None

    def set_callback(self, callback):
        """set a callback to be run by the ticker fn every `interval`"""
        self.callback = callback

    # second arg is incase using an outside timer that passes arg
    def ticker_exec(self, _=None):
        """
        fn that checks every `time_step` if interval has been reached.

        if passed interval, get new reading for dexcom and use callback if set.
        """
        self.count += self.time_step

        if self.count >= self.interval and not self.updating:
            self.updating = True

            self.get_reading()

            if self.callback:
                self.callback()

            timestamp = self.datetime
            # add 5:20 min
            future_datetime = timestamp + timedelta(seconds=320)
            interval = (future_datetime - datetime.now(timezone.utc)).seconds

            # TODO:
            #   - this is where to check for stale data and handle refresh
            #   - need a way to have bg data shown as stale

            # if time has passed, try again every 15s
            self.interval = max(15, interval)
            self.count = 0
            self.updating = False

    def start_ticker(self):
        """ticker loop"""
        while True:
            time.sleep(self.time_step)
            self.ticker_exec()

    def start(self):
        """start the ticker loop"""
        self.start_ticker()
