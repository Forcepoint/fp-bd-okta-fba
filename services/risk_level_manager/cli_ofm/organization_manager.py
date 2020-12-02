
import requests
import time
from org_manager.okta_fp_manager import *


class OrgManager:
    def __init__(self, parser):
        self._args = None
        self._parser = parser

    def __call__(self, args):
        self._args = args
        result, error_message = config.set_configs(self._args.config_file)
        if result is False:
            error_message = "Failed in loading config file: {}".format(error_message)
            logger.error(self, error_message)
            self._parser.error(error_message)
        self.start_service()

    def start_service(self):
        result = risk_level.register_with_connector()
        if requests is False:
            # retry for 3 times before given up
            for i in range(3):
                time.sleep(5)
                result = risk_level.register_with_connector()
                if result:
                    break
        if result is False:
            error_message = "Failed to register with the connector"
            logger.error(self, error_message)
            self._parser.error(error_message)
        ip_address, port = config.SELF_ADDRESS.split(":")
        app_org_mgr.run(port=port, debug=False, host=ip_address)


