from flask import Blueprint, render_template, request
from .auth import protect, withName
from . import certsdbwrapper as certdb
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

certs = Blueprint('certs', __name__)

@certs.route('/', methods = ['GET','POST'])
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    cur,conn = certdb.open()
    merits = {}
    parts = {}
    events = creds["Events"]
    for event in events:
        merits[event] = certdb.getMerits(event)
        parts[event] = certdb.getParts(event)
    apps = certdb.getAppr()
    certdb.close((cur,conn))
    print(apps[0])
    print(*apps[1:], sep="\n")
    return render_template("certs.html", uuid=UUID, name=NAME, merits=merits, parts=parts, apps=apps)