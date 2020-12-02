import json


class Config:
    def __init__(self):
        self.TOKEN = None
        self.ORG_URL = None
        self.LOG_LOCATION = None
        self.USER_APP_ADDRESS = None
        self.ORG_NAME = None
        self.LOG_FORMAT = '%(asctime)s - %(levelname)s -  %(message)s'
        self.ERROR_CODE_ONE = 1
        self.ERROR_CODE_ZERO = 0
        self.ERROR_CODE_EXIT = 100
        self.ROSE_API_URL = None
        self.MDS_API_URL = None
        self.FBA_API_URL = None
        self.ENTITY_CSV_PATH = None
        self.APPLICATION_PATH = None

    def set_configs(self, config_file):
        with open(config_file) as f:
            data = json.load(f)
            try:
                self.LOG_LOCATION = data["logs_directory"] + "/user_app.logs"
                self.USER_APP_ADDRESS = data["user_app_portal"]
                self.ORG_NAME = data["org_name"]
                self.TOKEN = data["org_token"]
                self.ORG_URL = data["organization_url"]
                self.FBA_API_URL = data["fba_api"]
                self.ROSE_API_URL = data["rose_api"]
                self.MDS_API_URL = data["mds1_api"]
                self.ENTITY_CSV_PATH = data["logs_directory"] + "/er.csv"
                self.APPLICATION_PATH = data["application_directory"]

                return True, ""
            except KeyError as e:
                return False, e.args[0]




