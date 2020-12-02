import json


class Config:
    def __init__(self):
        self.LOG_LOCATION = None
        self.CONNECTOR_ADDRESS = None
        self.SELF_ADDRESS = None
        self.USER_APP_ADDRESS = None
        self.ORG_NAME = None
        self.GROUPS_NAME = None
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s -  %(message)s'
        self.ERROR_CODE_ONE = 1
        self.ERROR_CODE_ZERO = 0
        self.ERROR_CODE_EXIT = 100
        self.APPLICATION_PATH = None

    def set_configs(self, config_file):
        with open(config_file) as f:
            data = json.load(f)
            try:
                self.LOG_LOCATION = data["logs_directory"] + "/risk_level_manager.logs"
                self.CONNECTOR_ADDRESS = data["connector_portal"]
                self.SELF_ADDRESS = data["risk_level_manager_portal"]
                self.USER_APP_ADDRESS = data["user_app_portal"]
                self.ORG_NAME = data["org_name"]
                self.GROUPS_NAME = data["risk_level_groups"]
                self.APPLICATION_PATH = data["application_directory"]
                return True, ""
            except KeyError as e:
                return False, e.args[0]



