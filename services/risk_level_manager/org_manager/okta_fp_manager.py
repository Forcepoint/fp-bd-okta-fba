from flask import Flask, request, jsonify
import json
from collections import namedtuple
from lib_ofm.risklevel import RiskLevel
from lib_ofm.config import Config
from lib_ofm.logger import Logger

app_org_mgr = Flask(__name__)
config = Config()
logger = Logger(config)

risk_level = RiskLevel(config, logger)


@app_org_mgr.route("/submit", methods=["POST"])
def store_risk_levels():
    """
    store the incoming risk level into a buffer
    :return: response
    """
    user_data = request.json
    user_data = json.loads(user_data)
    if user_data == "":
        return jsonify({"Error": "the body of the request should not be empty"}), 400
    error_code, error_message, response_data = risk_level.process_risk_level(user_data)
    if error_code != 0 or error_message != "":
        return jsonify({"error": error_message}), 400
    else:
        return jsonify(response_data), 201

