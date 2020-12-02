#
# Author:  Dlo Bagari
# created Date: 12-10-2019
import sqlite3
from sqlite3 import Error
from time import sleep
from sys import exit
from lib_consumer.logger import Logger


class DataBaseHandler:
    def __init__(self, database_location, org, user_utils, config):
        self._config = config
        self._location = database_location
        self._user_utils = user_utils
        self._org = org
        self._connect = None
        self._cursor = None
        self._log = Logger(self._config)
        self._connect_to_database()
        # TODO: capture the returned value
        self._create_tables()

    def handle_message(self, message, publisher):
        """
        check if the user is exist in the database, if not insert it. if the user is exist, update the user_app risk level
        :param message:
        :param publisher: the publisher object
        :return: boolean, boolean: to send notifications to connector
        """
        # check if user is exists in database

        user_id = message.get("user_id", None)
        if user_id is None:
            self._log.critical(self, "User ID is not exist in the received message")
            return False
        # id user not exists, insert the user to database and notify User API which will create all required entities
        result, first_name, last_name = self._get_user_name(user_id)
        if result is False:
            return result
        if self.is_user_exists(user_id) is False:
            result, user_org_id = self._org.has_user((first_name, last_name))
            # the user is not belong to the organization
            if result is False:
                return False
            error_code, error_message, group_data = publisher.send_notification(message, self._config.ORG_NAME,
                                                                                user_org_id,
                                                                                first_name, last_name,
                                                                                "")
            if error_code == 0:
                result = self._insert_user(user_org_id, self._config.ORG_NAME, group_data, message)
                sleep(1)
            if result is False:
                self._log.error(self, f":{self.handle_message.__name__} method: failed to insert a user into database")
                return result
            return True
        else:
            result, user_org_id, current_user_risk_level, group_name = self.get_user_risk_level(user_id)
            if result is True:

                if int(current_user_risk_level) != int(message["risk_level"]):
                    # send notification
                    error_code, error_message, group_data = publisher.send_notification(message, self._config.ORG_NAME,
                                                                                        user_org_id,
                                                                                        first_name, last_name,
                                                                                        group_name)
                    print("---------------")
                    print(error_code, error_message, group_data)
                    if error_code == 0:
                        result = self._update_risk_level(user_org_id, message["risk_level"],
                                                         group_data["new_group_name"]["profile"]["name"].lower(),
                                                         group_data["new_group_name"]["id"])
                        if result is True:
                            return result
                return True
            return False

    def _connect_to_database(self):
        try:
            self._connect = sqlite3.connect(self._location)
            self._cursor = self._connect.cursor()
        except Error as e:
            self._log.error(self, e)
            print("Error: {}: {}".format(self.__class__.__name__, e.args[0]))
            #exit(self._config.ERROR_CODE_ONE)

    def _create_tables(self):
        """
        Create required tables if they are not exists
        :return: boolean
        """
        try:
            result = self._cursor.execute(self._config.CREATE_USER_TABLE)
            self._connect.commit()
            # submit all exists user's name to Organization object
            submit_result = self.submit_exists_user()
            if submit_result is False:
                self._log.error(self, "Failed to submit all exists user_app in database to the Organization object")
            return False if result is None else True
        except Error as e:
            self._log.error(self, e)
            print("Error: {}: {}".format(self.__class__.__name__, e.args[0]))
            #exit(self._config.ERROR_CODE_ONE)

    def insert_row(self, user_id, first_name, last_name, user_email, login_name,
                   group_name, group_id, risk_level, timestamp, org_name):
        try:
            result = self._cursor.execute(self._config.INSERT_INTO_USERS,
                                          (user_id, first_name, last_name, user_email, login_name,
                                           group_name, group_id, risk_level, timestamp, org_name))
            self._connect.commit()
            return False if result is None else True
        except Error as e:
            self._log.error(self, e)
            return False

    def _insert_user(self, user_org_id, org_name, group_data, message):
        """
        insert a user into the database
        :return: boolean
        """
        status_code, user = self._user_utils.get_user_by_id(user_org_id)
        if status_code != 200:
            self._log.critical(self, f"Failed to get the user object from User API: {user['error']}")
            return False
        return self._add_user(user, org_name,  group_data, message)

    def _add_user(self, user, org_name,  group_data, message):
        """
        adds a user to database
        :param user: the user object
        :param: the message object
        :return:
        """
        len(user)
        user_id = user['id']
        user_email = user['profile']['email']
        first_name = user['profile']['firstName']
        last_name = user['profile']['lastName']
        login_name = user['profile']['login']
        group_name = group_data["new_group_name"]["profile"]["name"].lower()
        group_id = group_data["new_group_name"]["id"]
        # ask User API for user Entities
        return self.insert_row(user_id, first_name, last_name,
                               user_email, login_name,
                               group_name, group_id,
                               message['risk_level'],
                               message['timestamp'], org_name)

    def _get_user_name(self, user_identifier):
        """
        extract user first name and last name from the user identifier
        :param user_identifier: the user's identifier
        :return: fist_name, last_name
        """
        user_name = user_identifier.strip().split('@')[0]
        delimiter = " "
        if "." in user_name:
            delimiter = "."
        if "," in user_name:
            delimiter = ','
        parts = user_name.split(delimiter)
        if len(parts) == 2:
            return True, parts[0], parts[1]
        else:
            return False, "", ""


    def is_user_exists(self, user_identifier):
        """
        check if a user is exists in the database
        :param user_identifier:
        :return:boolean
        """
        result, first_name, last_name = self._get_user_name(user_identifier)
        row = self.get_user_row(first_name, last_name)
        if len(row) > 1:
            self._log.critical(self, "multiple user_app exists in the table with the same user identifier")
        if len(row) == 0:
            return False
        return True

    def get_user_risk_level(self, user_identifier):
        """
        query the user's risk level
        :param user_identifier: the user's id
        :return:boolean, user_id, risk level
        """
        tesult, first_name, last_name = self._get_user_name(user_identifier)
        row = self.get_user_row(first_name, last_name)
        if len(row) == 0:
            self._log.critical(self, "failed to query the risk level for an exist user")
            return False, "", ""
        row_to_dict = self.row_to_dict(row[0])
        return True, row_to_dict["user_id"], row_to_dict["risk_level"], row_to_dict["group_name"]

    def get_user_row(self, first_name, last_name):
        """
        query a user information form the user's table
        :param first_name:
        :param last_name:
        :return: database record
        """
        query = f'SELECT * FROM {self._config.USER_TABLE_NAME}' \
                f' WHERE first_name = "{first_name}" AND last_name = "{last_name}"'
        result = self._cursor.execute(query)

        return self._cursor.fetchall()



    def row_to_dict(self, row):
        """
        Create a dict from the row
        :param row: a database record
        :return: dictionary
        """
        result = {}
        for idx, col in enumerate(self._cursor.description):
            result[col[0]] = row[idx]
        return result

    def _update_risk_level(self, user_org_id, risk_level_value, group_name_value, group_id_value):
        """
        Update the user risk level
        :param user_org_id: the user's org ID
        :param risk_level: the new risk level
        :return: boolean
        """
        update_risk_level = f"UPDATE {self._config.USER_TABLE_NAME} SET risk_level = {risk_level_value} WHERE user_id = '{user_org_id}'"
        update_group_name = f"UPDATE {self._config.USER_TABLE_NAME}" \
                            f" SET group_name = '{group_name_value}' WHERE user_id = '{user_org_id}'"
        update_group_id = f"UPDATE {self._config.USER_TABLE_NAME}" \
                            f" SET group_id = '{group_id_value}' WHERE user_id = '{user_org_id}'"
        try:
            for query in [update_risk_level, update_group_name, update_group_id]:
                self._cursor.execute(query)
            self._connect.commit()
        except Error as e:
            self._log.error(self, e.args[0])
            return False
        return True

    def submit_exists_user(self):
        query = "SELECT first_name, last_name FROM {}".format(self._config.USER_TABLE_NAME)
        try:
            self._cursor.execute(query)
            rows = self._cursor.fetchall()
            for rows in rows:
                self._org.add_user(rows)
        except Error as e:
            self._log.error(self, e.args[0])
            return False
        return True

