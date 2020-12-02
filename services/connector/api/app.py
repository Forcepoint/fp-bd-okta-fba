#
# functionality: provides FRSTful API for connector
# Author:  Dlo Bagari
# created Date: 12-10-2019

from flask import Flask, request, jsonify
import json
from lib.registry import Registry
from lib.config import Config
from lib.logger import Logger
from lib.execmd import ExeCmd
app = Flask(__name__)
config = Config()
logger = Logger(config)
exec_cmd = ExeCmd()
registry = Registry(config, logger, exec_cmd)


@app.route('/', methods=["POST", "GET"])
def send_endpoints():
    endpoints = {"register": {"endpoint": "/register", "usage": "To register an Organization Manager with connector"},
                 "publisher": {"endpoint": "/publish", "usage": "To submit risk levels for user_app to the connector."
                                                                " connector will forward these risk level to a "
                                                                "Organization Manager"}}
    return jsonify(endpoints), 200


@app.route('/register', methods=["POST"])
def register_org():
    org_data = request.json
    if org_data == "":
        return jsonify({"Error": "the body of the request should not be empty"}), 400
    for key in {"org_name", "endpoint"}:
        if key not in org_data.keys():
            return jsonify({"Error": f"sent data is missing '{key}' key"}), 400
    if "data_format" in org_data:
        data_format = org_data["data_format"]
    else:
        data_format = "json"
    error_code, error_message = registry.add_org_to_registry(org_data["org_name"],
                                                             org_data["endpoint"],
                                                             data_format)
    if error_code != 0:
        return jsonify({"Error": "Server Failed to process "
                                 "the request, check the servers logs for more information"}), 304
    else:
        return jsonify(), 201


@app.route("/publish", methods=["POST"])
def publish_to_org():
    rec_data = request.json
    rec_data_json = json.loads(rec_data)
    if rec_data == "":
        return jsonify({"Error": "the body of the request should not be empty"}), 400
    for key in "org_name user_id  first_name last_name risk_level timestamp group_name".split():
        if key not in rec_data_json.keys():
            return jsonify({"Error": f"sent data is missing '{key}' key"}), 400
    result, json_file = registry.send_data_to_org(rec_data_json)
    if result is True:
        return jsonify(json_file), 202
    return json_file({"Error": "Failed in sending data to organization manager"}), 304


if __name__ == "__main__":
    app.run()
