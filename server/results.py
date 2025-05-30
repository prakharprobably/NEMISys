from flask import Blueprint, render_template, request
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
