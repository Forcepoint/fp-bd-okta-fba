#
# Author:  Dlo Bagari
# created Date: 12-10-2019
from flask import Flask, request, jsonify
from flask import jsonify
from user_api.userapi import UserAPI
from user_api.group_api import GroupApi
from lib_user.logger import Logger
from lib_user.config import Config
from lib_user.entity import Entity
import json

config = Config()
logger = Logger(config)
user_api = UserAPI(config, logger)
group_api = GroupApi(config, logger)
entity = Entity(config)
app = Flask(__name__)


@app.route("/user")
def get_user():
    return user_api.get_user()


@app.route("/user/<user_id>")
def get_user_by_id(user_id):
    return user_api.get_user(user_id)


@app.route("/user/filter")
def filter_user():
    first_name = request.args.get("first_name", None)
    last_name = request.args.get("last_name", None)
    return user_api.find_user_by_name(first_name, last_name)


@app.route("/group/filter")
def filter_group_by_name():
    name = request.args.get("name", None)
    if name is None:
        return jsonify({"error": "missing parameter name"}), 400
    return group_api.filter_group_by_name(name)


@app.route("/groups/change", methods=["POST"])
def change_group():
    data = json.loads(request.json)
    return group_api.change_group(data["user_id"], data["current_group"], data["new_group"])


# TODO: in process
@app.route("/entity", methods=["POST"])
def handle_entity():
    data = request.json
    error_code, result, entity_id = entity.handle_notification(data)
    if error_code == config.ERROR_CODE_ZERO and result is True:
        return jsonify({"entity_id": entity_id}), 201
    else:
        return jsonify({"error": "Failed in handling the request"}), 400

