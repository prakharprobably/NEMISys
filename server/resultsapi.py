from . import resultsdbwrapper as resdb
from flask import Blueprint, request, jsonify
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

allowedKeys=creds["APIKeys"]

discauth= Blueprint('discauth', __name__)
@discauth.route('/<username>')
def checkUser(username):
    APIKey = request.cookies.get("APIKey")
    if APIKey not in allowedKeys:
        return jsonify({}), 401
    print(username)
    curconn=dauth.open()
    events = creds["Events"]
    data = {}
    for event in events:
        pass
    resdb.close(curconn=curconn)
    if not data:
        return jsonify({}),404
    else:
        return jsonify(data),200