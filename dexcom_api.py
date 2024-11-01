import json
from pydexcom import Dexcom


class DexcomAPI:
    def __init__(self, dexcom_dir):
        self.credentials = self.load_credentials(dexcom_dir + "dexcom_credentials.json")

        self.reading = None
        self.bg_value = None
        self.previous_bg_value = None
        self.delta = None
        self.datetime = ""
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

    def get_reading(self):
        self.get_current_glucose_reading()
        self.create_status()
        self.colorize_status()
