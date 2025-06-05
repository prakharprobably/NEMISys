from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .auth import protect, withName
from . import resultsdbwrapper as resdb
from . import eventdbwrapper as evdb
from . import statusdbwrapper as statusdb
from . import certsdbwrapper as certdb
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
def raw(UUID, NAME):
    cur,conn = resdb.open()
    results = {}
    events = creds["Events"]
    results["Overalls"] = resdb.getOverallRes()
    for event in events:
        results[event] = resdb.getEventRes(event=event, round="finals")
    resdb.close((cur,conn))
    return render_template("results.html", results = results)

@results.route('/mod', methods=['GET', 'POST'])
@protect(['EI', 'TC'])
@withName
def home(UUID, NAME):
    cur, conn = resdb.open()
    resdb.close((cur, conn))
    prelds = creds["preldEvents"]
    events = creds["Events"]
    results = {}

    if request.method == 'GET':
        results["Overalls"] = resdb.getOverallRes()
        for event in events:
            data = evdb.getResTable(event, "finals")
            resInd = data[0].index("points")
            results[event] = data
        return render_template(
            '/modres.html',
            results=results,
            uuid=UUID,
            name=NAME,
            resInd=resInd
        )

    elif request.method == 'POST':
        ecur, econn = evdb.open()
        markBuf = {}

        # Overalls updates
        for key in request.form:
            val = request.form[key].strip()
            if key.startswith("Overalls_"):
                sid, field = key.split("_")[1:]
                try:
                    val = int(val)
                except ValueError:
                    continue
                if field == "points":
                    resdb.setOveralls(sid, val)
                elif field == "firsts":
                    resdb.setFirsts(sid, val)
                elif field == "seconds":
                    resdb.setSeconds(sid, val)
                elif field == "thirds":
                    resdb.setThirds(sid, val)
        for event in events:
            data = evdb.getResTable(event, "finals")[1:]  # Skip header
            all_ids = {row[0] for row in data[1:]}
            checked_ids = {
                key.rsplit('_', 2)[1]
                for key in request.form
                if key.endswith("_pref") and request.form[key] == "1"
            }
            unchecked_ids = all_ids - checked_ids
            for sid in checked_ids:
                points = int(request.form.get(f"{event}_{sid}_points", 0))
                print(points)
                evdb.markRes(ecur, event, sid, points, "finals", True)
            for sid in unchecked_ids:
                points = int(request.form.get(f"{event}_{sid}_points", 0))
                print(points)
                evdb.markRes(ecur,event, sid, points, "finals", False)
        econn.commit()
        certdb.genMerits()
        certdb.genParts()
        certdb.genAppr()
        ecur.close()
        econn.close()
        return redirect(url_for('results.raw'))



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