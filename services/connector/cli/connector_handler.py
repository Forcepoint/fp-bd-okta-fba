#
# Author:  Dlo Bagari
# created Date: 12-10-2019

from api.app import *


class ConnectorHandler:
    def __init__(self, parser):
        self._args = None
        self._parser = parser

    def __call__(self, args):
        self._args = args
        result, error_msg = config.set_configs(self._args.config_file)
        if result is False:
            error_msg = "Failed in loading the config file: {}".format(error_msg)
            logger.error(self, error_msg)
            self._parser.error(error_msg)
        address, port = config.SELF_ADDRESS.split(":")
        app.run(port=int(port), debug=False, host=address)
