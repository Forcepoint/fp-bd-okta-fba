#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import json


class Config:
    def __init__(self):
        self.TOKEN = None
        self.ORG_URL = None
        self.ORG_NAME = None
        self.TIMESTAMP_FILE = None
        self.BUFFER_DIRECTORY = None
        self.LOG_DIRECTORY = None
        self.DESTINATION_API_URL = None
        self.APPLICATION_DIRECTORY = None
        self.USER_APP_API = None
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s -  %(message)s'
        self.SKIP_URL_ACK = 100
        self._ERROR_CODE_ONE = 1
        self.ERROR_CODE_ZERO = 0

    def set_configs(self, config_file):
        with open(config_file) as f:
            data = json.load(f)
            try:
                self.TOKEN = data["org_token"]
                self.ORG_NAME = data["org_name"]
                self.DESTINATION_API_URL = "https://{}:9000/event".format(data["fba_api"])
                self.APPLICATION_DIRECTORY = data["application_directory"]
                self.TIMESTAMP_FILE = self.APPLICATION_DIRECTORY + "/timestamp"
                self.BUFFER_DIRECTORY = self.APPLICATION_DIRECTORY + "/events_buffer"
                self.LOG_DIRECTORY = "{}/events_app.logs".format(data["logs_directory"])
                self.ORG_URL = data["organization_url"]
                self.USER_APP_API = data["user_app_portal"]
                return True, ""

            except KeyError as e:
                return False, e.args[0]
