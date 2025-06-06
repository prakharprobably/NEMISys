from flask import Blueprint, render_template, request
from .auth import protect, withName
from . import statusdbwrapper as statusdb

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

status=Blueprint('status', __name__)
@status.route('/')
@protect(['EI','TC', 'SI'])
@withName
def home(UUID, NAME):
    print(f"STATUS@{UUID}: attempted access")
    cur,conn = statusdb.open()
    data = [('Event', 'Status')]
    data.extend([(row[0], statusdb.statuses[row[1]]) for row in statusdb.getStatusTable()])
    statusdb.close((cur,conn))
    return render_template('table.html', uuid=UUID, name=NAME, data=data)