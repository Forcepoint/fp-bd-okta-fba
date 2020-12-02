import argparse
from cunsumer.consumer_manager import ConsumerManager
from .create_service import CreateService


class CliArgsParse:
    def __init__(self, pro_name):
        self._pro_name = pro_name
        self._parser = argparse.ArgumentParser(prog=pro_name)
        self._consumer_manager = ConsumerManager()
        self._create_service = CreateService(self._parser)
        self._build_args()

    def _build_args(self):
        subparsers = self._parser.add_subparsers(title="sub-commands")
        consumer_cli = subparsers.add_parser("consumer", description="Runs kafka Consumer Manager to process messages")
        # TODO: in process
        service_cli = subparsers.add_parser("service",
                                            description="create Systemd Service for consumer_manager.service")

        consumer_cli.add_argument("--client-id", "-ci", action="store", dest="client_id",
                                  help="the client ID", default="client_okta_1")
        consumer_cli.add_argument("--session-timeout", "-st", action="store", type=int, default=6000,
                                  help="Session timeout in ms", dest="session_timeout")
        consumer_cli.add_argument("--config-file", "-c", action="store", dest="config_file", required=True,
                                  help="REQUIRED: the config_consumer file path")
        consumer_cli.set_defaults(function=self._consumer_manager)
        self._parser.set_defaults(function=self.default)

        service_cli.add_argument("--start", "-s", action="store_true",
                                 default=False, dest="start", help="Start "
                                                                   "systemd service(okta_consumer_manager.service")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="okta_consumer_manager", dest="name", help="the service name,default name is "
                                                                                    "okta_consumer_manager.service")
        service_cli.add_argument("--config-file", "-c", action="store", dest="config_file",
                                 help="the config file path", required=True)
        service_cli.set_defaults(function=self._create_service)

    def get_parser(self):
        return self._parser

    def default(self, *args):
        yield "Error: missing a sub-command. run {} -h for help".format(self._pro_name), ""
