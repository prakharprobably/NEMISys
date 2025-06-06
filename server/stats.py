from flask import Blueprint, render_template, request
from .auth import protect, withName
from . import statsdbwrapper as statsdb
import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

stats = Blueprint('stats', __name__)

@stats.route('/', methods = ['GET','POST'])
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    cur,conn = statsdb.open()
    parts = statsdb.getParticipation(cur)
    onsiteParts = statsdb.getOnsiteCount(cur)
    regSchools = statsdb.getTotalSchoolCount(cur)
    partSchools = statsdb.getParticipatingSchoolCount(cur)
    onsiteSchools = statsdb.getOnsiteSchoolCount(cur)
    statsdb.close((cur,conn))
    return render_template("stats.html", parts=parts, onsiteParts=onsiteParts, regSchools=regSchools, partSchools=partSchools, onsiteSchools=onsiteSchools, uuid=UUID, name=NAME)