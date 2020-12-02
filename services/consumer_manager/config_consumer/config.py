import json


class Config:
    def __init__(self):
        self.ORG_NAME = ""
        self.ERROR_CODE_ONE = 1
        self.ERROR_TO_EXIT = 100
        self.ERROR_CODE_ZERO = 0
        self.USER_API_URL = None
        self.EMPTY_STRING = ""
        self.LOG_LOCATION = None
        self.DATABASE_LOCATION = None
        self.CONNECTOR_PUBLISH_API_URL = None
        self.KAFKA_BROKER = None
        self.KAFKA_TOPIC = None
        self.KAFKA_GROUP_NAME = None
        self.APPLICATION_PATH = None
        self.CLIENT_CA_CER = None
        self.CLIENT_CER = None
        self.CLIENT_KEY = None
        self.KEY_STORE_PASS = None

        self.LOG_FORMAT = '%(asctime)s - %(levelname)s -  %(message)s'
        self.USER_TABLE_NAME = "user_app"
        self.NOT_BELONG_TO_ORG = "User is not belong to Organization"
        self.CREATE_USER_TABLE = """CREATE TABLE IF NOT EXISTS {} (
                            id integer PRIMARY KEY,
                            user_id text NOT NULL,
                            first_name text NOT NULL,
                            last_name text NOT NULL,
                            email text NOT NULL ,
                            login text NOT NULL ,
                            group_name NOT NULL,
                            group_id NOT NULL,
                            risk_level integer NOT NULL,
                            time_stamp integer NOT NULL,
                            org_name text NOT NULL);""".format(self.USER_TABLE_NAME)
        self.INSERT_INTO_USERS = '''INSERT INTO {}(user_id, first_name, last_name,
                       email, login, group_name, group_id, risk_level, time_stamp, org_name)
                        VALUES (?,?,?,?,?,?,?,?,?,?)'''.format(self.USER_TABLE_NAME)

    def set_configs(self, config_file):
        with open(config_file) as f:
            data = json.load(f)
            try:
                self.APPLICATION_PATH = data["application_directory"]
                self.ORG_NAME = data["org_name"]
                self.KAFKA_BROKER = data["kafka_broker"]
                self.KAFKA_TOPIC = data["kafka_topic_name"]
                self.KAFKA_GROUP_NAME = data["kafka_group_name"]
                self.USER_API_URL = "http://{}/user".format(data["user_app_portal"])
                self.DATABASE_LOCATION = "{}/database/{}_database." \
                                         "db".format(data["application_directory"], self.ORG_NAME)
                self.CONNECTOR_PUBLISH_API_URL = "http://{}/publish".format(data["connector_portal"])
                self.LOG_LOCATION = "{}/consumer_manager.logs".format(data["logs_directory"])
                self.CLIENT_CA_CER = data["client-ca.cer"]
                self.CLIENT_CER = data["client.cer"]
                self.CLIENT_KEY = data["client.key"]
                self.KEY_STORE_PASS = data["key_store_pass"]
                return True, ""

            except KeyError as e:
                return False, e.args[0]

