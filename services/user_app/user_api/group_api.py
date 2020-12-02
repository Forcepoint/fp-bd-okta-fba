#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from flask import jsonify


class GroupApi:
    def __init__(self, config, logger):
        self._group = None
        self._config = config
        self._logger = logger

    def filter_group_by_name(self, group_name):
        error_code, error_message, group = self._group.filter_groups_by_name(group_name)
        if error_code != 0:
            self._logger.error(self, error_message)
            return jsonify({"error": error_message}), 400
        else:
            return jsonify(group), 200

    def set_group(self, group):
        self._group = group

    def change_group(self, user_id, current_group, new_group, terminate_session=True):
        error_code, error_message, group = self._group.change_group(user_id, current_group, new_group,
                                                                    terminate_session=terminate_session)
        if error_code != 0 or len(error_message) != 0:
            self._logger.error(self, error_message)
            return jsonify({"error": error_message, "status": "failed"}), 400
        else:
            return jsonify(group), 201
