#
# functionality: class for parsing eventcli options
# Author:  Dlo Bagari
# created Date: 24-09-2019

import argparse
from .event import Event

from .createservice import CreateService
from lib_event.config import Config


class CliArgs:
    def __init__(self, pro_name):
        self.__parser = argparse.ArgumentParser(prog=pro_name)
        self.__config = Config()
        self.event = Event(self.__parser, self, self.__config)
        self.create_service = CreateService(self.__parser)
        # self.generator = Generator(self.__parser, self.__config)
        self.sender = None

        self._build_args()

    def _build_args(self):
        """
        Build the parser
        :return: None
        """
        # create two sub commands: service, events
        subparsers = self.__parser.add_subparsers(title="sub-commands")
        service_cli = subparsers.add_parser("service", description="create Systemd Service for okta.service")
        events_cli = subparsers.add_parser("events", description="Pull events from okta org and send them to FBA")
        """
        # the generator sub command is used only for generating events.
        event_generator_cli = subparsers.add_parser("generator", description="Generate events for test purpose only "
                                                                             "DO NOT USE THIS IN REAL ENVIRONMENT")
        event_generator_cli.add_argument("--number", "-n", action="store", dest="number",
                                         type=int, help="The number of events to generate", required=True)
        event_generator_cli.add_argument("--multi-locations", "-ml", action="store", type=int, dest="multi_location",
                                         help="Number of events to be generated from different locations")
        event_generator_cli.add_argument("--view", "-v", action="store_true",  dest="view", default=False,
                                         help="Display selected timestamps and some more information")
        event_generator_cli.add_argument("--config-file", "-c", action="store",
                                         dest="config_file", help="config file path", required=True)
        event_generator_cli.set_defaults(function=self.generator)
        """
        # create service eventcli
        service_cli.add_argument("--start", "-s",  action="store_true",
                                 default=False, dest="start", help="Start systemd service(okta_event.service)")
        service_cli.add_argument("--name", "-n", action="store",
                                 default="okta_event", dest="name",
                                 help="the service name, default name is 'okta_event'")
        service_cli.add_argument("--config-file", "-c", action="store",
                                 required=True, dest="config_file",
                                 help="the config file path")
        service_cli.set_defaults(function=self.create_service)

        # create options for events sub-command

        events_cli.add_argument("--view", "-v",
                                action="store_true",
                                default=False,
                                dest="view",
                                help="Display the process. Use this only to view the process.")
        events_cli.add_argument("--map-okta", "-m",
                                action="store_true",
                                default=True,
                                dest="map_okta",
                                help="Map okta logs schema to RIM schema")
        events_cli.add_argument("--frequency", "-f",
                                type=int, default=5,
                                dest="frequency", help="Time to sleep between each two requests in seconds "
                                                       "the default value is 5 seconds")
        events_cli.add_argument("--buffer-max", "-b",
                                type=int, default=100,
                                dest="buffer", help="the number of logs which can be stored on disk "
                                                    "the default value is 100 seconds")
        events_cli.add_argument("--config-file", "-c", action="store",
                                dest="config_file", help="config file path", required=True)
        events_cli.set_defaults(function=self.event)

    def get_parser(self):
        """
        return the built parser
        :return: parser
        """
        return self.__parser
