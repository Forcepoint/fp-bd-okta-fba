#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import requests
import json


class Registry:
    def __init__(self, config, logger, exec_cmd):
        self._logger = logger
        self._execute_cmd = exec_cmd
        self._config = config

    def add_org_to_registry(self, org_name, end_point, data_format='json'):
        """
        Add an organisation to the registry. with this action an organisation will register itself with connector
        :param org_name: the organisation name
        :param end_point: the organisation end point, where to sent data
        :param data_format: the type of the data which the organisation will expect.
        :return: error_code, error_message
        """
        try:
            error_code, result = self.is_organisation_exists(org_name)
            if error_code == 0 and result is True:
                return self.update_registry_records(org_name, end_point, data_format)
            with open(self._config.REGISTRY_FILE_PATH, "a") as f:
                record = ",".join([org_name, end_point, data_format])
                f.write(record)
                f.write("\n")
                return self._config.ERROR_CODE_ZERO, ""
        except Exception as e:
            self._logger.error(self, e.args[0])
            return self._config.ERROR_CODE_ONE, e.args[0]

    def _read_registry_records(self):
        """
        Reads all records from organisation.csv and
        returns a dictionary in format {org_name: {endpoint: value, data_format: value}}
        :return: return error_code, error_message, dict
        """
        records = {}
        try:
            with open(self._config.REGISTRY_FILE_PATH) as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) > 2:
                        records[parts[0]] = {"endpoint": parts[1], "data_format": parts[2]}
                return self._config.ERROR_CODE_ZERO, "", records
        except Exception as e:
            self._logger.error(self, e.args[0])
            return self._config.ERROR_CODE_ONE, e.args[0]

    def update_registry_records(self, org_name, end_point, data_format):
        """
        update an exists registry record
        :return: error_code, error_message
        """
        record = ",".join([org_name, end_point, data_format])
        cmd = f"sed -i 's@^{org_name},.*@{record}@g' {self._config.REGISTRY_FILE_PATH}"
        output, error = self._execute_cmd.run(cmd)
        if len(error.strip()) != 0:
            self._logger.error(self, f":Command Error: {error}")
            return self._config.ERROR_CODE_ONE, error
        else:
            return self._config.ERROR_CODE_ZERO, ""

    def is_organisation_exists(self, org_name):
        """
        check if an organisation is already exists in organisation.csv
        :return: error_code, boolean
        """
        cmd = f"grep -E '^{org_name}' {self._config.REGISTRY_FILE_PATH}"
        output, error = self._execute_cmd.run(cmd)
        if len(output.strip()) == 0:
            return self._config.ERROR_CODE_ZERO, False
        elif len(error.strip()) != 0:
            self._logger.error(self, f":Command Error: {error}")
            return self._config.ERROR_CODE_ONE, False
        else:
            return self._config.ERROR_CODE_ZERO, True

    def send_data_to_org(self, data_rcv):
        """
        submit data to the organization's manager end point
        :param data_rcv: the data which will be sent
        :return: boolean, json_file
        """
        org_name = data_rcv["org_name"]
        error_code, endpoint, data_format = self.get_org_manager_endpoint(org_name)
        if error_code != self._config.ERROR_CODE_ZERO:
            self._logger.critical(self, f"Failed in getting a record for {org_name} from registry records")
            return False, {}
        if not endpoint.startswith("http://") or endpoint.startswith("https://"):
            endpoint = "http://" + endpoint
        response = requests.request("POST", endpoint, json=json.dumps(data_rcv))
        if response.status_code != 202:
            errors = response.json()
            if "Error" in errors.keys():
                self._logger.error(self, errors["Error"])
                return False, {}
        return True, response.json()

    def get_org_manager_endpoint(self, org_name):
        """
        extract the organization record from registry
        :param org_name: the organization name
        :return: error_code, endpoint_url, data_format
        """
        cmd = f"grep -E '^{org_name},' {self._config.REGISTRY_FILE_PATH}"
        output, error = self._execute_cmd.run(cmd)
        if len(output.strip()) == 0:
            self._logger.error(self, f"not record found for {org_name} in the registry records")
            return self._config.ERROR_CODE_ONE, "", ""
        parts = output.strip().split(',')
        if len(parts) < 3:
            self._logger.error(self, f"the record for {org_name} is not correct in the registry records")
            return self._config.ERROR_CODE_ONE, "", ""
        return self._config.ERROR_CODE_ZERO, parts[1], parts[2]
