import json
import time
from datetime import datetime, timedelta, timezone
from pydexcom import Dexcom


class Ticker:
    def __init__(self, time_step):
        self.time_step = time_step
        self.interval = time_step
        self.count = 0

        self.updating = False
        self.delta = None
        self.datetime = ""

        self.app_runner = False

    def set_callback(self, callback):
        self.callback = callback

    def ticker_exec(self):
        self.count += self.time_step

        if self.count >= self.interval and not self.updating:
            # print(datetime.now())
            self.updating = True
            self.callback()

            timestamp = self.datetime
            future_datetime = timestamp + timedelta(seconds=310)  # Add 5:10 min
            interval = (future_datetime - datetime.now(timezone.utc)).seconds

            self.interval = interval
            self.count = 0
            # TODO: for now stop from running more than once
            # self.updating = False

    def start_ticker(self):
        while True:
            time.sleep(self.time_step)
            self.ticker_exec()

    def run(self):
        if self.callback:
            self.start_ticker()
        else:
            print("must set callback")


class DexcomHandler:
    def __init__(self, dexcom_dir, time_step):
        self.ticker = Ticker(time_step)

        self.credentials = self.load_credentials(dexcom_dir + "dexcom_credentials.json")
        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"

        self.reading = None
        self.bg_value = None
        self.previous_bg_value = None

        self.status = ""
        self.color_status = ""
        self.colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "end": "\033[0m",
        }

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
            # TODO: logging, print for now
            print(f"Error setting up client: {e}")
            self.reading = "ERROR"

    def get_current_glucose_reading(self):
        self.reading = self.dexcom.get_current_glucose_reading()
        self.ticker.datetime = self.reading.datetime

    def create_status(self):
        bg = self.reading
        value = bg.value
        arrow = bg.trend_arrow
        print(bg)

        self.bg_value = value
        self.status = f"{value} {arrow}"

    def colorize_status(self):
        value = self.bg_value
        colors = self.colors
        end = colors["end"]

        if 80 <= value <= 180:
            color = colors["green"]
        elif value >= 181:
            color = colors["red"]
        elif value <= 79:
            color = colors["yellow"]
        else:
            color = colors["blue"]

        self.color_status = f"{color}{self.status}{end}"

    def write_state(self):
        with open(self.state_file, "w") as f:
            f.write(self.status)

        with open(self.state_color_file, "w") as f:
            f.write(self.color_status)

    def get_reading(self):
        self.get_current_glucose_reading()
        self.create_status()
        self.colorize_status()
        self.write_state()

    def set_callback(self, callback):
        self.ticker.set_callback(callback)

    def run(self):
        self.ticker.run()
