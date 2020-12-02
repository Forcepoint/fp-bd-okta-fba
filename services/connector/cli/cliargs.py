
#
# functionality: connector argparse class
# Author:  Dlo Bagari
# created Date: 12-10-2019

import argparse
from .connector_handler import ConnectorHandler
from .create_service import CreateService


class CliArgs:
    def __init__(self, pro_name):
        self._pro_name = pro_name
        self._parser = argparse.ArgumentParser(prog=pro_name)
        self._connector_handler = ConnectorHandler(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the connector")
        service_cli = subparsers.add_parser("service", description="create Systemd Service for okta_connector.service")

        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="the config file path", required=True)
        run_cli.set_defaults(function=self._connector_handler)

        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start systemd service(okta_connector.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="okta_connector", dest="name", help="the service name,"
                                                                             " default name is 'okta_connector'")
        service_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                                 help="the config file path", required=True)
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        """
        returns the argparse object
        :return: parser
        """
        return self._parser
