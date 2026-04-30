import logging
import json

from pydexcom import Dexcom
from .ticker import Ticker

_log = logging.getLogger(__name__)


def log(msg):
    _log.info(f"[ GDBG ] {msg}")


def debug(msg):
    _log.debug(f"[ Ticker ] {msg}")


class GDBG:
    """class to manage data from Dexcom using `pydexcom`"""

    def __init__(self, dexcom_dir, time_step, callback, create_state=False):
        ## initialize Ticker
        self.ticker = Ticker(time_step, self.get_reading, callback)

        self.state_file = dexcom_dir + "bg_status.txt"
        self.state_color_file = dexcom_dir + "bg_color_status.txt"
        self.credentials_file = dexcom_dir + "dexcom_credentials.json"
        self.credentials = self.load_credentials(self.credentials_file)

        self.initialized = False
        self.reading = None
        self.bg_value = 0
        self.previous_bg_value = 0
        self.delta = 0
        self.datetime = None
        self.is_reading_stale = False

        self.create_state = create_state
        self.status = None
        self.short_status = None

        self.login_dexcom()

    def get_reading(self):
        """`internal_callback' to be used by Ticker to get readings"""
        self.get_current_glucose_reading()
        self.update_data()
        self.create_status()

        return self.is_reading_stale

    def load_credentials(self, path):
        """load credentials from json for dexcom"""
        try:
            with open(path, "r") as f:
                return json.load(f)

        except Exception as error:
            raise Exception(f"unable to load credentials: {error}")

    def login_dexcom(self):
        """use loaded credentials to login to dexcom"""
        credentials = self.credentials

        try:
            self.dexcom = Dexcom(
                username=credentials["username"], password=credentials["password"]
            )

        except Exception as error:
            raise Exception(f"failed to login into dexcom: {error}")

    def get_current_glucose_reading(self):
        """
        get current glucose reading

        catches one instance of a thrown `pydexcom.errors.SessionError` if session id expired, and attempts to get a new session id and retries

        (https://github.com/gagebenne/pydexcom/blob/9bd35b2597513ba6e13ce4e3211a0e8f6517cf33/pydexcom/__init__.py#L341)
        """

        log("Authenticating with Dexcom...")

        try:
            # check if session is still valid
            self.dexcom._validate_session_id()

        except Dexcom.errors.SessionError:
            # attempt to update expired session id
            self.dexcom._session()

        log("Requesting current available reading, within the last 10 minutes...")

        ## current available glucose reading, within the last 10 minutes
        reading = self.dexcom.get_current_glucose_reading()

        if reading:
            debug(
                f"""New reading:
                \t\t\t\t\tvalue: {reading.value}
                \t\t\t\t\ttrend: {reading.trend}
                \t\t\t\t\tarrow: {reading.trend_arrow}
                \t\t\t\t\tdatetime: {reading.datetime}"""
            )

            self.is_reading_stale = False
            self.reading = reading

        else:
            debug("Reading is stale \n\t\t\t\t\t\t\t- - -")
            self.is_reading_stale = True

    def update_data(self):
        """handler to update the datetime, delta, and current bg value"""
        if self.is_reading_stale:
            self.update_stale_bg()
            self.delta = 0

        else:
            self.update_datetime()
            self.update_current_bg()
            self.update_delta()

    def update_datetime(self):
        """update the datetime used by Ticker"""
        self.datetime = self.reading.datetime
        self.ticker.set_datetime(self.datetime)

    def update_stale_bg(self):
        """update current bg value to reflect stale data"""
        self.bg_value = "---"

    def update_current_bg(self):
        """update current bg value"""
        self.bg_value = self.reading.value

    def update_delta(self):
        if self.initialized:
            delta = str(self.bg_value - self.previous_bg_value)
            if int(delta) > 0:
                delta = f"+{delta}"

        else:
            delta = 0
            self.initialized = True

        self.delta = delta
        self.previous_bg_value = self.bg_value

    def create_status(self):
        """create status to be used in cli or elsewhere'"""
        if self.is_reading_stale:
            self.status = self.short_status = "- - -"

        else:
            bg = self.reading
            value = bg.value
            arrow = bg.trend_arrow
            delta = self.delta
            timestamp = self.datetime

            self.status = f"{value} {delta} {arrow} '{timestamp}'"
            self.short_status = f"{value} {arrow}"

        if self.create_state:
            self.write_state()

    def write_state(self):
        """write status to file"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                f.write(self.status)

            log(f"Status: {self.status}")
            log(f"State file updated: {self.state_file}")

        except Exception as error:
            raise Exception(f"failed to write status file: {error}")

    def start(self):
        """start ticker that updates dexcom reading every `interval`"""
        log("Starting Ticker")
        self.ticker.start()
