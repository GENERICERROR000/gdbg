import json
import time
from datetime import datetime, timedelta, timezone
from pydexcom import Dexcom


class Ticker:
    def __init__(self, time_step):
        self.time_step = time_step
        self.interval = 0
        self.count = 0
        self.updating = False
        self.delta = None
        self.datetime = None
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def ticker_exec(self):
        self.count += self.time_step

        if self.count >= self.interval and not self.updating:
            self.updating = True

            if self.callback:
                self.callback()

            timestamp = self.datetime
            future_datetime = timestamp + timedelta(seconds=320)  # Add 5:20 min
            interval = (future_datetime - datetime.now(timezone.utc)).seconds

            # if time has passed, try again every minute
            self.interval = max(60, interval)
            self.count = 0
            self.updating = False

    def start_ticker(self):
        while True:
            time.sleep(self.time_step)
            self.ticker_exec()

    def run(self):
        self.start_ticker()


class DexcomHandler:
    def __init__(self, dexcom_dir, time_step):
        self.ticker = Ticker(time_step)

        self.credentials = self.load_credentials(dexcom_dir + "dexcom_credentials.json")
        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"

        self.reading = None
        self.bg_value = None
        self.previous_bg_value = None
        self.datetime = None
        self.status = None

        self.login_dexcom()

    def load_credentials(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def login_dexcom(self):
        credentials = self.credentials

        try:
            self.dexcom = Dexcom(
                username=credentials["username"], password=credentials["password"]
            )
        except Exception as e:
            print(f"Error setting up client: {e}")
            self.reading = "ERROR"

    def get_current_glucose_reading(self):
        self.reading = self.dexcom.get_current_glucose_reading()

    def update_time_and_delta(self):
        self.ticker.datetime = self.reading.datetime
        self.datetime = self.reading.datetime

        if not self.previous_bg_value:
            self.previous_bg_value = self.reading.value
        else:
            self.previous_bg_value = self.bg_value

    def create_status(self):
        bg = self.reading
        value = bg.value
        arrow = bg.trend_arrow

        self.bg_value = value
        self.status = f"{value} {arrow}"
        # NOTE: for debug
        # print(bg)

    def write_state(self):
        with open(self.state_file, "w") as f:
            f.write(self.status)

    def get_reading(self):
        self.get_current_glucose_reading()
        self.update_time_and_delta()
        self.create_status()
        self.write_state()

    def set_callback(self, callback):
        self.ticker.set_callback(callback)

    def run(self):
        self.ticker.run()
