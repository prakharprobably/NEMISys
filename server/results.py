from flask import Blueprint, render_template, request, jsonify
from .auth import protect, withName
from . import resultsdbwrapper as resdb
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

results = Blueprint('results', __name__)

@results.route('/raw', methods = ['GET','POST'])
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    cur,conn = resdb.open()
    results = {}
    events = creds["Events"]
    results["Overalls"] = resdb.getOverallRes()
    for event in events:
        results[event] = resdb.getEventRes(event=event, round="finals")
    resdb.close((cur,conn))
    return render_template("results.html", results = results)

@results.route('/api')
def getRes():
    allowedKeys = creds["APIKeys"]
    APIKey = request.cookies.get("APIKey")
    if APIKey not in allowedKeys:
        return jsonify({}), 401
    curconn=resdb.open()
    data = {}
    resdb.close(curconn=curconn)
    events = creds["Events"]
    for event in events:
        data.update(resdb.getWinningParts(event))
    if not data:
        return jsonify({}),404
    else:
        return jsonify(data),200


@results.route('/api/finals')
def getFinRes():
    allowedKeys = creds["APIKeys"]
    APIKey = request.cookies.get("APIKey")
    if APIKey not in allowedKeys:
        return jsonify({}), 401
    curconn=resdb.open()
    data = {}
    resdb.close(curconn=curconn)
    events = creds["Events"]
    for event in events:
        data.update(resdb.getWinningParts(event))
    if not data:
        return jsonify({}),404
    else:
        return jsonify(data),200

@results.route('/api/prelims')
def getPriRes():
    allowedKeys = creds["APIKeys"]
    APIKey = request.cookies.get("APIKey")
    if APIKey not in allowedKeys:
        return jsonify({}), 401
    curconn=resdb.open()
    data = {}
    resdb.close(curconn=curconn)
    events = creds["preldEvents"]
    for event in events:
        data.update(resdb.getQualifyingParts(event))
    print(data)
    if not data:
        return jsonify({}),404
    else:
        return jsonify(data),200