from flask import Blueprint, render_template,request,redirect,url_for,flash
from . import staffdbwrapper as sdb
from . import eventdbwrapper as evdb
from .auth import protect, withName
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

events=Blueprint('events', __name__)
@events.route('/')
@protect(['EI','TC', 'SI'])
@withName
def redir(UUID, NAME):
    print(f"REDIR:{UUID}({NAME}) attempted connection")
    cur,conn = sdb.open()
    event = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    return redirect(url_for('events.home', event=uEvent))

@events.route('/<event>')
@protect(['EI','TC', 'SI'])
@withName
def home(UUID, NAME, event):
    cur,conn = sdb.open()
    uEvent = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    if uEvent not in (event, 'All'):
        return redirect(url_for('events.home', event=uEvent))
    else:
        return render_template('/events/events.html', event=uEvent, uuid=UUID, name=NAME)

@events.route('/<event>/attendance')
@protect(['EI','TC', 'SI'])
@withName
def attendance(UUID, NAME, event):
    cur,conn = sdb.open()
    uEvent = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    if uEvent == 'Virtual Warriors':
        pass
    else:
        if uEvent in (event, 'All'):
            if request.method == 'GET':
                data = evdb.getAttTable(uEvent)
                attInd = data[0].index("attendance")
                print(*data, sep="\n")
                return render_template('/events/eattendance.html', data=data, uuid=UUID, name=NAME, event=uEvent, attInd=attInd)
            if request.method == 'POST':
                ecur,econn = evdb.open()
                data = evdb.getAttTable(uEvent)
                all_ids = {row[0] for row in data[1:]}
                checked_ids = {int(key.split('_')[1]) for key in request.form if key.startswith('attendance_')}
                unchecked_ids = all_ids - unchecked_ids
            
            for pid in checked_ids:
                evdb.markAtt(ecur, pid, True)
            for pid in unchecked_ids:
                evdb.markAtt(ecur, pid, False)
            confirm(conn)
            close((cur,conn))
            data = evdb.getAttTable(uEvent)
            return render_template('/events/eattendance.html', data=data, uuid=UUID, name=NAME, event="uEvent")
        else:
            return redirect(url_for(f'/events/'))