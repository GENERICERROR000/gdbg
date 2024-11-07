import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pydexcom import Dexcom


class Ticker:
    """class to create a timer that executes fn every `interval`"""

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

    def ticker_exec(self):
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

            # if time has passed, but no new reading, try again every minute
            self.interval = max(60, interval)
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


class DexcomHandler:
    """class to manage using `pydexcom`"""

    def __init__(self, dexcom_dir, time_step):
        self.ticker = Ticker(self.get_reading, time_step)

        self.credentials = self.load_credentials(dexcom_dir + "dexcom_credentials.json")
        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"

        self.reading = None
        self.bg_value = 0
        self.previous_bg_value = 0
        self.datetime = None
        self.status = None
        self.short_status = None

        self.login_dexcom()

    def load_credentials(self, path):
        """load credentials from json for dexcom"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as error:
            raise Exception("unable to load credentials: " + str(error))

    def login_dexcom(self):
        """use loaded credentials to login to dexcom"""
        credentials = self.credentials

        try:
            self.dexcom = Dexcom(
                username=credentials["username"], password=credentials["password"]
            )
        except Exception as error:
            raise Exception("failed to login into dexcom: " + str(error))

    def get_current_glucose_reading(self):
        """
        get current glucose reading

        catches one instance of a thrown `pydexcom.errors.SessionError` if session id expired, and attempts to get a new session id and retries

        (https://github.com/gagebenne/pydexcom/blob/9bd35b2597513ba6e13ce4e3211a0e8f6517cf33/pydexcom/__init__.py#L341)
        """
        try:
            # check if session is still valid
            self.dexcom._validate_session_id()

            self.reading = self.dexcom.get_current_glucose_reading()
        except Dexcom.errors.SessionError:
            # attempt to update expired session id
            self.dexcom._session()

            self.reading = self.dexcom.get_current_glucose_reading()

    def update_time(self):
        """update the datetime used by the ticker"""
        self.ticker.datetime = self.reading.datetime
        self.datetime = self.reading.datetime

    def update_delta(self):
        self.previous_bg_value = self.bg_value

        delta = str(self.bg_value - self.previous_bg_value)
        if int(delta) > 0:
            delta = f"+{delta}"

        self.delta = delta

    def update_current_bg(self):
        """update current bg value"""
        self.bg_value = self.reading.value

    def update_data(self):
        """handler to update the datetime, delta, and current bg value"""
        self.update_time()
        self.update_delta()
        self.update_current_bg()

    def write_state(self):
        """write status to file"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                f.write(self.status)
        except Exception as error:
            raise Exception("failed to write status file: " + str(error))

    def create_status(self):
        """create status: '[bg] [trend arrow]'"""
        bg = self.reading
        value = bg.value
        arrow = bg.trend_arrow
        delta = self.delta
        timestamp = self.datetime

        self.status = f"{value} {delta} {arrow} '{timestamp}'"
        self.short_status = f"{value} {arrow}"
        self.write_state()

    def get_reading(self):
        """callback to be used by ticker to get readings"""
        self.get_current_glucose_reading()
        self.update_data()
        self.create_status()

    def set_callback(self, callback):
        """fn to set additional callback to be run by ticker every `interval`"""
        self.ticker.set_callback(callback)

    def start(self):
        """start ticker that updates dexcom reading every `interval`"""
        self.ticker.start()
