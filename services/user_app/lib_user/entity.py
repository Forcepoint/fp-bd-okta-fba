from lib_user.execmd import ExeCmd


class Entity:
    def __init__(self, config):
        self._config = config
        self._exec_cmd = ExeCmd()
        self._monitored = {}

    def handle_notification(self, data):
        # check if the use is monitored
        entity_id = self._monitored.get((data["first_name"], data["last_name"], data["email_address"]))
        if entity_id is not None:
            return self._config.ERROR_CODE_ZERO, True, entity_id
        error_code, result, entity_id = self._is_monitored(data)
        if error_code == 0 and result is False:
            result = self._set_monitor(data)
            if result is True:
                error_code, result, entity_id = self._is_monitored(data)
        if error_code == self._config.ERROR_CODE_ZERO and result is True:
            self._monitored[(data["first_name"], data["last_name"], data["email_address"])] = entity_id
        return error_code, result, entity_id

    def _is_monitored(self, data):
        # get all exists monitored entities
        cmd = 'curl -X GET "https://{}:9500/v1/entity/list/monitored" ' \
              '-H "accept: application/json" -k'.format(self._config.ROSE_API_URL)
        output, error = self._exec_cmd.run(cmd)
        if len(output) == 0:
            return self._config.ERROR_CODE_ONE, False, ""
        else:
            user_first_name = data["first_name"].lower()
            user_last_name = data["last_name"].lower()
            for entity in output["entities"]:
                actor_name = entity["actor_id"].split()
                if len(actor_name) == 2:
                    if actor_name[0].lower() == user_first_name \
                            and actor_name[1].lower() == user_last_name:
                        return self._config.ERROR_CODE_ZERO, True, entity["id"]
        return self._config.ERROR_CODE_ZERO, False, ""

    def _set_monitor(self, data):
        result = self._set_entity(data)
        if result is True:
            cmd = 'curl -k -XPOST -H \'Content-Type: application/json\' -d \'' \
                  '{"name": "Monitored Entity", "value": "TRUE"}\'' \
                  ' \'%s\'' % "https://{}:8080/reference/actor/{}%20{}/attribute/boolean".format(self._config.MDS_API_URL,
                                                                                                 data["first_name"],
                                                                                                 data["last_name"])
            output, error = self._exec_cmd.run(cmd)
            if len(output) != 0 and isinstance(output, dict):
                result = output.get("boolean")
                if result is not None and len(result) != 0 and result[0]["value"] is True:
                    return True
                return False
            return False
        return False

    def _set_entity(self, data):
        csv_file_path = self._config.ENTITY_CSV_PATH
        csv_content = 'DISAMBIGUATION,ACTOR\n{} {},{}\n'.format(data["first_name"],
                                                                data["last_name"],
                                                                data["email_address"])
        with open(csv_file_path, 'w') as f:
            f.write(csv_content)
        cmd = 'curl -k -XPOST https://{}:9000/resolution_key/upload?apply=true ' \
              '-F file=@{};type=text/csv'.format(self._config.FBA_API_URL, csv_file_path)
        output, error = self._exec_cmd.run(cmd)
        if len(output) != 0 and isinstance(output, dict):
            status = output.get("status")
            if status is not None and status == "SUCCESS":
                return True
            return False
        return False



