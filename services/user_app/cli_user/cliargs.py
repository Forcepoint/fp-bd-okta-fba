import argparse
from cli_user.app_handler import AppHandler
from .create_service import CreateService


class CliArgs:
    def __init__(self, pro_name):
        self._pro_name = pro_name
        self._parser = argparse.ArgumentParser(prog=pro_name)
        self._org_manager = AppHandler(self._parser)
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        run_cli = subparsers.add_parser("run",
                                        description="Runs the organization risk level manager")

        run_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                             help="REQUIRED: The config file path", required=True)
        run_cli.set_defaults(function=self._org_manager)
        service_cli = subparsers.add_parser("service",
                                            description="creates okta_user.service Systemd Service")
        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start systemd service"
                                                                   "(okta_user.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="okta_user", dest="name",
                                 help="the service name, default name is 'okta_user'")
        service_cli.add_argument("--config-file", "-c", action="store",
                                 required=True, dest="config_file",
                                 help="the config file path")
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        return self._parser




