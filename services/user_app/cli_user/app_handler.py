from user.user import User
from user.groups import Groups
from user_api.flaskapi import *


class AppHandler:
    def __init__(self, parser):
        self._args = None
        self._parser = parser

    def __call__(self, args):
        self._args = args
        result, error_message = config.set_configs(self._args.config_file)
        if result is False:
            error_message = "Failed to load config file: {}".format(error_message)
            logger.error(self, error_message)
            self._parser.error(error_message)
        user_api.set_user(User(config.TOKEN, config.ORG_URL))
        group_api.set_group(Groups(config.TOKEN, config.ORG_URL))
        ip_address, port = config.USER_APP_ADDRESS.split(":")
        app.run(port=int(port), debug=False, host=ip_address)
