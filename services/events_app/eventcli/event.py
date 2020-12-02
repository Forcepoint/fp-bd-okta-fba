#
# functionality: class for system log requests
# Author:  Dlo Bagari
# created Date: 24-09-2019

from datetime import datetime
import json
import requests
from os import path
from time import sleep
import re
import sys
import os
import glob
import subprocess
from subprocess import Popen
import multiprocessing
from lib_event.logger import Logger
from lib_event.user_api import UserApi

ERROR_CODE_ZERO = 0
ERROR_CODE_ONE = 1
EMPTY_STRING = ""
RETRY = 2
BREAK_TIME = 30


class Sender(multiprocessing.Process):
    def __init__(self, from_directory, to_url, logger, config, user_api):
        super().__init__()
        self.__url = to_url
        self.__from_directory = from_directory
        self.name = "sender_fba"
        self.count = 0
        self._logger = logger
        self._configs = config
        self._user_api = user_api
        self._monitored = {}

    def run(self):
        try:
            while True:
                sleep(5)
                urls = glob.glob("{}/*.json".format(self.__from_directory))
                for url in urls:
                    with open(url, "r") as f:
                        context = f.read().strip()
                        cmd = 'curl -XPOST -H"Content-Type:' \
                              'application/json" {} -k -d \'{}\''.format(self.__url, context)
                        if len(context.strip()) == 0:
                            self.remove(url)
                            continue
                        output, error = self.execute_cmd(cmd)
                        if output is None:
                            self._logger.error(self, error.decode())
                            print('\033[93m Error: {}\033[m'.format(error.decode()))
                            if "unexpected EOF while looking" in error.decode():
                                self.remove(url)
                            continue
                        if len(output) != 0:
                            if "acknowledged" in output:
                                print("{}: {}".format(url, output["acknowledged"]))
                                if output["acknowledged"] is True:
                                    error_code, entity_id = self._user_api.acknowledge_user_app(url)
                                    if error_code != self._configs.ERROR_CODE_ZERO:
                                        print('\033[93m Error: {}\033[m'.format(entity_id))
                                    print("monitored:{}".format(entity_id))
                                    self.remove(url)
                            elif "code" in list(output.keys()) and int(output["code"]) == 400:
                                print('\033[93m Error: {}\033[m'.format(output["message"]))
                            else:
                                for retry in range(RETRY):
                                    print("Retrying to send the event {}".format(url))
                                    output, error = self.execute_cmd(cmd)
                                    if "acknowledged" in output:
                                        print("{}: {}".format(url, output["acknowledged"]))
                                        if output["acknowledged"] is True:
                                            error_code, entity_id = self._user_api.acknowledge_user_app(url)
                                            if error_code != self._configs.ERROR_CODE_ZERO:
                                                print('\033[93m Error: {}\033[m'.format(entity_id))
                                            print("monitored:{}".format(entity_id))
                                            self.remove(url)
                                        break
                                    sleep(BREAK_TIME)
                                print('\033[93m Error: Failed to sent an event: {}\033[m'.format(url))
                sleep(5)

        except KeyboardInterrupt or AttributeError:
            sys.exit(0)

    @staticmethod
    def execute_cmd(cmd):
        process = Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, errors = process.communicate()
        if len(output.decode()) == 0:
            return None, errors
        return json.loads(output), errors

    def remove(self, url):
        os.remove(url)
        self.count += 1


class Event:
    def __init__(self, parser, cli_args, config):
        self.__args = None
        self.__log_storage = set()
        self.__parser = parser
        self.cli_args = cli_args
        self._config = config
        self._logger = None
        self._user_api = None

    def __call__(self, args):
        self.__args = args
        result, message = self._config.set_configs(self.__args.config_file)
        if result is False:
            self.__parser.error("Error in the config file: {}".format(message))
        self._logger = Logger(self._config)
        self._user_api = UserApi(self._config)
        try:
            if os.path.exists(self._config.BUFFER_DIRECTORY) is False:
                os.mkdir(self._config.BUFFER_DIRECTORY)
            if self._config.DESTINATION_API_URL.startswith("http://") \
                    or self._config.DESTINATION_API_URL.startswith("https://"):
                rcv_url = self._config.DESTINATION_API_URL
            else:
                rcv_url = "https://{}".format(self._config.DESTINATION_API_URL)
            to_fba = Sender(self._config.BUFFER_DIRECTORY, rcv_url, self._logger, self._config, self._user_api)
            to_fba.start()
            self.cli_args.sender = to_fba

            for error_code, error_message in self.pull_events():
                if error_code == ERROR_CODE_ONE:
                    to_fba.terminate()
                    self.__parser.error(error_message)
        except FileNotFoundError:
            error_message = "the given path '{}' is not a valid path".format(self._config.BUFFER_DIRECTORY)
            self._logger.error(self, error_message)
            raise self.__parser.error(error_message)


    def pull_events(self):
        """
        pull events and process them
        :return:
        """
        try:
            events, used_header = self.request_events()
            if events.status_code != 200:
                self._logger.error("Error in response from organization with status code {}".format(events.status_code))
                raise self.__parser.error("Error in response with status code {}".format(events.status_code))
            for event in events.json():
                error_code, error_message = self.process_event(event)
                if error_code != 0:
                    raise self.__parser.error(error_message)
            if self.__args.view is True:
                if len(self.__log_storage):
                    yield ERROR_CODE_ZERO, "{} Logs has been received already".format(len(self.__log_storage))
                yield ERROR_CODE_ZERO, "\nwaiting for new Logs....."
            self.listen_to_events(events, used_header)
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)

    @staticmethod
    def display_notification(event):
        """
        display the content of the new arrived events
        :param event: the event object
        :return: none
        """
        now = datetime.now()
        now = now.isoformat()[:-3] + 'Z'
        msg_format = "\033[1;31;40m Received a new Log on {}: \033[0m".format(now)
        print(msg_format)
        print(event)

    def map_to_rim(self, event):
        """
        convert okta schema to RIM schema
        :param event: event object
        :return: dictionary
        """
        browsers = self.get_browser_info(event)
        rim_json = {"timestamp": event["published"],
                    "type": "Authentication",
                    "entities": [],
                    "attributes": [{"type": "String", "name": "Time Stamp", "value": event["published"]}]}
        label = self.get_label(event)
        if label is not None:
            rim_json["labels"] = [label]
        subject = self.get_subject(event)
        if subject is not None:
            rim_json["subject"] = subject
        source_event_id = self.get_source_event_id(event)
        if source_event_id is not None:
            rim_json["source_event_id"] = source_event_id
        roles = [self.get_app, self.user, self.domain, self.vendor, self.source_ip,
                 self.source_country, self.source_city, self.user_id, self.email_address]
        attributes = [self.browser_name, self.browser_version, self.device_name, self.user_agent, self.event_id,
                      self.success, self.session_id_attribute, self.signature, self.event_type,
                      self.app_instance,
                      self.app_user]

        for role in roles:
            result = role(event)
            if result is not None:
                rim_json["entities"].append(result)
        for attr in attributes:
            result = attr(event)
            if result is not None:
                rim_json["attributes"].append(result)
        success = self.success(event)
        if success is not None and success["value"] is False:
            reason = self.reason(event)
            if reason is not None:
                rim_json["attributes"].append(reason)
        return rim_json

    def email_address(self, event):
        try:
            email_address = event["actor"]["alternateId"]
            if email_address is None:
                return email_address
            return {"role": "Email", "entities": [email_address]}
        except Exception:
            return None

    def get_label(self, event):
        try:
            label = event["eventType"].split('.')
            if len(label) > 2:
                return " ".join(label[:2])
            elif len(label) > 0:
                return label[0]
            else:
                return None
        except Exception:
            return None


    def extract_agents(self, agents_string):
        """
        extract all browser agents from a given rawUserAgent string
        :param agents_string: rawUserAgent
        :return: list
        """
        agents = re.sub(r"\(.*\)", "", agents_string.lower())
        return agents.strip().split()


    def get_app_name(self, event):
        """
        extract the application name from okta event
        :param event: the okta event
        :return: string
        """
        app_name = [None, None, None]
        app_name[0] = event["client"]["userAgent"]["os"]
        if event["target"] is not None and len(event["target"]) != 0:
            for target in event["target"]:
                if target["type"] == "AppInstance":
                    app_name[1] = target["displayName"]
                if target["type"] == "AppUser":
                    app_name[2] = target["alternateId"]
        return app_name

    def get_session_id(self, event):
        """
        extract the session id from okta event
        :param event: the okta event
        :return: string
        """
        try:
            return event["authenticationContext"]["externalSessionId"]
        except Exception:
            return None

    def get_browser_info(self, event):
        """
        extract the browser information from okta event
        :param event: the okta event
        :return: dictionary {browser: version}
        """
        try:
            if event["client"]["userAgent"]["browser"].lower() == "unknown":
                return None
            agents = self.extract_agents(event["client"]["userAgent"]["rawUserAgent"])
            browsers = {}
            for i in agents:
                parts = i.strip().split("/")
                browsers[parts[0]] = parts[1]
            return browsers
        except Exception:
            return None

    def get_outcome(self, event):
        """
        extract the outcome result from an okta event
        :param event: the okta event
        :return:
        """
        reason = event["outcome"]["reason"]
        if event["outcome"]["result"] is None or (event["outcome"]["result"] is None and reason.lower() == "unknown"):
            return None, None
        if event["outcome"]["result"].lower() == "success":
            return True, reason
        else:
            return False, reason

    def process_event(self, event):
        """
        Process an event by converting it to RIM schema and save it.
        :param event: json object
        :type: json
        :return: error_code, error_message
        """
        if event["actor"]["type"] != "SystemPrincipal" and "lifecycle.update" not in event["eventType"]:
            to_be_saved = event
            if event["uuid"] not in self.__log_storage:
                self.__log_storage.add(event["uuid"])
                if self.__args.map_okta is True:
                    to_be_saved = self.map_to_rim(event)
            else:
                return ERROR_CODE_ZERO, EMPTY_STRING
            if self._config.BUFFER_DIRECTORY is not None and len(self._config.BUFFER_DIRECTORY) != 0:
                with open("{}/{}:{}:{}.json".format(self._config.BUFFER_DIRECTORY, event["actor"]["displayName"],
                                                    event["actor"]["alternateId"], event["uuid"]), "w") as f:
                    all_logs = glob.glob("{}/*.json".format(self._config.BUFFER_DIRECTORY))
                    if len(all_logs) > self.__args.buffer:
                        self.wait_for_buffer()
                    json.dump(to_be_saved, f)
        return ERROR_CODE_ZERO, EMPTY_STRING

    def request_events(self):
        """
        send HTTP request to obtain events
        :return: Response_Object, used_http_header
        """
        start_time = None
        if self._config.ORG_URL.startswith("http://"):
            url = "https://{}/api/v1/logs".format(self._config.ORG_URL.replace("https://", ""))
        else:
            url = "https://{}/api/v1/logs".format(self._config.ORG_URL)
        headers = {'Authorization': 'SSWS {}'.format(self._config.TOKEN),
                   "Accept": "application/json",
                   "Content-Type": "application/json"}
        params = {"sortOrder": "ASCENDING"}
        param_sort_only = {"sortOrder": "ASCENDING"}
        if path.exists(self._config.TIMESTAMP_FILE):
            with open(self._config.TIMESTAMP_FILE) as f:
                start_time = f.read().strip()
        if start_time is not None:
            params["after"] = start_time
        response = requests.get(url, headers=headers, params=params)
        return response, headers

    def listen_to_events(self, events, headers):
        """
        listen to new events, if there is any new events, process them.
        :param events: the okta event
        :param headers: used header for all http requests
        :return: Success:boolean, reason:string
        """
        param_after = 0
        while 'next' in events.links:
            events = requests.get(events.links['next']['url'], headers=headers)
            next_url = events.links['next']['url']
            param_after_value = next_url.split("&after=")[-1]
            param_after_update = float(param_after_value.replace("_", "."))
            if param_after_update > param_after:
                with open(self._config.TIMESTAMP_FILE, "w") as f:
                    f.write(param_after_value)
                param_after = param_after_update
            for event in events.json():
                if event["actor"]["type"] != "SystemPrincipal" and "lifecycle.update" not in event["eventType"]:
                    if event["uuid"] not in self.__log_storage:
                        self.__log_storage.add(event["uuid"])

                        with open("{}/{}:{}:{}.json".format(self._config.BUFFER_DIRECTORY, event["actor"]["displayName"],
                                                            event["actor"]["alternateId"], event["uuid"]), "w") as f:
                            all_logs = glob.glob("{}/*.json".format(self._config.BUFFER_DIRECTORY))
                            if len(all_logs) > self.__args.buffer:
                                self.wait_for_buffer()
                            json.dump(self.map_to_rim(event), f)
                        if self.__args.view is True:
                            self.display_notification(event)

            sleep(self.__args.frequency)

    def wait_for_buffer(self):
        if self.__args.view is True:
            print("The buffer is Full.. Waiting for events to be moved to FBA")
        while True:
            sleep(self.__args.frequency)
            if len(glob.glob("{}/*.json".format(self._config.BUFFER_DIRECTORY))) < self.__args.buffer:
                break
        if self.__args.view is True:
            print("The waiting process is Done")

    def get_app(self, event):
        try:
            app = self.get_app_name(event)[0]
            if app is None or (app is not None and app.lower() == "unknown"):
                return None
            return {"role": "App", "entities": [app.replace("'", "")]}
        except Exception:
            return None

    def user_id(self, event):
        try:
            user_id = event["actor"]["id"]
            if user_id is None or (user_id is not None and user_id.lower() == "unknown"):
                return None
            return {"role": "User ID", "entities": [user_id]}
        except Exception:
            return None

    def user(self, event):
        try:
            value = event["actor"]["displayName"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "User", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def domain(self, event):
        try:
            value = self._config.ORG_URL
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Domain", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def vendor(self, event):
        return {"role": "Vendor", "entities": [self._config.ORG_NAME]}

    def source_ip(self, event):
        try:
            value = event["client"]["ipAddress"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source IP", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def session_id(self, event):
        try:
            value = event["authenticationContext"]["externalSessionId"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "session", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def source_country(self, event):
        try:
            value = event["client"]["geographicalContext"]["country"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source Country", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def source_city(self, event):
        try:
            value = event["client"]["geographicalContext"]["city"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"role": "Source City", "entities": [value.replace("'", "")]}
        except Exception:
            return None

    def browser_name(self, event):
        try:
            value = event["client"]["userAgent"]["browser"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Browser Name", "value": value.replace("'", "").lower()}
        except Exception:
            return None

    def browser_version(self, event):
        browsers = self.get_browser_info(event)
        try:
            value = browsers[event["client"]["userAgent"]["browser"].lower()] if browsers is not None else None
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Browser Version", "value": value.replace("'", "")}
        except Exception:
            return None

    def device_name(self, event):
        try:
            value = event["client"]["device"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Device Type", "value": value.replace("'", "")}
        except Exception:
            return None

    def user_agent(self, event):
        try:
            value = event["client"]['userAgent']['rawUserAgent']
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "User Agent", "value": value.replace("'", "").lower()}
        except Exception:
            return None

    def postcode(self, event):
        try:
            value = event["client"]['geographicalContext']["postalCode"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "postalCode", "value": value.replace("'", "")}
        except Exception:
            return None

    def event_id(self, event):
        try:
            value = event["uuid"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Event ID", "value": value.replace("'", "")}
        except Exception:
            return None

    def get_source_event_id(self, event):
        try:
            return event["uuid"]
        except Exception:
            return None

    def success(self, event):
        try:
            value = self.get_outcome(event)[0]
            if value is None:
                return None
            return {"type": "Boolean", "name": "Success", "value": value}
        except Exception:
            return None

    def reason(self, event):
        try:
            value = self.get_outcome(event)[1]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Reason", "value": value.replace("'", "")}
        except Exception:
            return None

    def session_id_attribute(self, event):
        try:
            value = self.get_session_id(event)
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Session ID", "value": value.replace("'", "")}
        except Exception:
            return None

    def signature(self, event):
        try:
            value = event["displayMessage"]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Signature", "value": value.replace("'", "")}
        except Exception:
            return None

    def get_subject(self, event):
        try:
            return event["displayMessage"]
        except Exception:
            return None

    def event_type(self, event):
        try:
            value = " ".join(event["eventType"].split(".")[1:])
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "Type", "value": value.replace("'", "")}
        except Exception:
            return None

    def app_instance(self, event):
        try:
            app = self.get_app_name(event)
            value = app[1]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "App instance", "value": app[1].replace("'", "")}
        except Exception:
            return None

    def app_user(self, event):
        try:
            app = self.get_app_name(event)
            value = app[2]
            if value is None or (value is not None and value.lower() == "unknown"):
                return None
            return {"type": "String", "name": "App instance User", "value": app[2].replace("'", "")}
        except Exception:
            return None
