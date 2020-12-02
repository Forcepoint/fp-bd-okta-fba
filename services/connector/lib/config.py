#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import json


class Config:
    def __init__(self):
        self.APPLICATION_PATH = None
        self.REGISTRY_FILE_PATH = None
        self.LOG_LOCATION = None
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s -  %(message)s'
        self.SELF_ADDRESS = None
        self.ERROR_CODE_ONE = 1
        self.ERROR_CODE_ZERO = 0

    def set_configs(self, config_file):
        with open(config_file) as f:
            data = json.load(f)
            try:
                self.REGISTRY_FILE_PATH = data["application_directory"] + "/organisation.csv"
                self.LOG_LOCATION = data["logs_directory"] + "/connector.logs"
                self.SELF_ADDRESS = data["connector_portal"]
                self.APPLICATION_PATH = data["application_directory"]
                return True, ""
            except KeyError as e:
                return False, e.args[0]
