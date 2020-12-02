#
# functionality: class for creating okta.service systemd service
# Author:  Dlo Bagari
# created Date: 01-10-2019

import subprocess
from subprocess import Popen
from os import system, path
from config_consumer.config import Config


class CreateService:
    def __init__(self, parser):
        self.__parser = parser
        self.__args = None
        self._config = Config()

    def __call__(self, args):
        self.__args = args
        self._config.set_configs(self.__args.config_file)
        result = self.is_service_exists(self.__args.name)
        if result is True:
            self.__parser.error("The service '{}' is already exists".format(self.__args.name))
        else:
            result = self._create_service(self.__args.name)
            if result is True:
                yield self._config.ERROR_TO_EXIT
        if self.__args.start is True:
            result, error_code = self.is_service_running(self.__args.name)
            if error_code == 1:
                self.__parser.error("problem with executing commands")
            if error_code == 0 and result is True:
                self.__parser.error("The service '{}' is already running".format(self.__args.name))
            system("systemctl daemon-reload")
            if self.__args.start is True:
                system("systemctl start {}.service".format(self.__args.name))

    @staticmethod
    def execute_cmd(cmd):
        process = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, errors = process.communicate()
        return output, errors

    def is_service_exists(self, name):
        service_path = "/etc/systemd/system/{}.service".format(name)
        return path.isfile(service_path)

    def is_service_running(self, name):
        cmd = ["systemctl",  "list-units"]
        output, errors = self.execute_cmd(cmd)
        output = output.strip()
        if len(output) != 0:
            output = output.split("\n")
            for line in output:
                if line.strip().startswith("{}.service ".format(name)):
                    return True, 0
            return False, 0
        return False, 1

    def _create_service(self, name):
        service = """
[Unit]
Description=Pull risk levels from kafka bus and send it to the connector
Wants=network-online.target
After=network.target network-online.target okta_user.service
Requires=okta_user.service

[Service]
ExecStart={}/scripts/consumer_manager_service.sh consumer -c {}

[Install]
WantedBy=multi-user.target
""".format(self._config.APPLICATION_PATH, self.__args.config_file)
        service_path = "/etc/systemd/system/{}.service".format(name)
        try:
            with open(service_path, "w") as f:
                f.write(service)
            system("chmod 644 {}".format(service_path))
            return True
        except Exception as e:
            self.__parser.error("Failed in creating systemd service: {}".format(e))

