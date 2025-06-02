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
    return redirect(url_for('events.home', event=event))

@events.route('/<event>')
@protect(['EI','TC', 'SI'])
@withName
def home(UUID, NAME, event):
    cur,conn = sdb.open()
    uEvent = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    prelds=creds["preldEvents"]
    if uEvent not in (event, 'All'):
        return redirect(url_for('events.home', event=uEvent))
    else:
        return render_template('/events/events.html', event=uEvent, uuid=UUID, name=NAME, preld= uEvent in prelds)
        

@events.route('/<event>/attendance/<round>', methods=['GET','POST'])
@protect(['EI','TC', 'SI'])
@withName
def attendance(UUID, NAME, event, round):
    cur,conn = sdb.open()
    uEvent = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    if uEvent in (event, 'All'):
        prelds = creds["preldEvents"]
        if uEvent not in prelds and round == "prelims":
            return(redirect(f'/events/'))
        if request.method == 'GET':
            data = evdb.getAttTable(uEvent,round)
            attInd = data[0].index("attendance")
            print(*data, sep="\n")
            return render_template('/events/eattendance.html', data=data, uuid=UUID, name=NAME, event=uEvent, attInd=attInd)
        if request.method == 'POST':
            ecur,econn = evdb.open()
            data = evdb.getAttTable(uEvent, round)
            print(*data, sep="\n")
            all_ids = {row[0] for row in data[1:]}
            checked_ids = {int(key.split('_')[1]) for key in request.form if key.startswith('attendance_')}
            unchecked_ids = all_ids - checked_ids
        for pid in checked_ids:
            evdb.markAtt(ecur,event, pid, True, round)
        for pid in unchecked_ids:
            evdb.markAtt(ecur,event, pid, False, round)
        evdb.genRes((ecur,econn),uEvent,round)
        econn.commit()
        ecur.close()
        econn.close()
        data = evdb.getAttTable(uEvent, round)
        return render_template('/events/eattendance.html', data=data, uuid=UUID, name=NAME, event="uEvent")
    else:
        return redirect(url_for(f'/events/'))


@events.route('/<event>/grade/<round>', methods=['GET','POST'])
@protect(['EI','TC', 'SI'])
@withName
def grade(UUID, NAME, event, round):
    cur,conn = sdb.open()
    uEvent = sdb.getEvent(cur=cur,uuid=UUID)
    sdb.close(conncur=(conn,cur))
    if uEvent in (event, 'All'):
        prelds = creds["preldEvents"]
        if uEvent not in prelds and round == "prelims":
            return(redirect(f'/events/'))
        if request.method == 'GET':
            data = evdb.getResTable(event,round)
            resInd = data[0].index("points")
            print(*data, sep="\n")
            return render_template('/events/results.html', data=data, uuid=UUID, name=NAME, event=uEvent, resInd=resInd)
        if request.method == 'POST':
            ecur,econn = evdb.open()
            data = evdb.getResTable(event, round)
            print(*data, sep="\n")
            print(request.form)
            for sid in request.form:
                evdb.markRes(ecur, event, sid, int(request.form[sid]), round)
        if round=="prelims":
            evdb.genAtt((ecur,econn),event,"finals")
        else:
            evdb.genWinTable(ecur, event)
        econn.commit()
        ecur.close()
        econn.close()
        data = evdb.getResTable(uEvent, round)
        return render_template('/events/results.html', data=data, uuid=UUID, name=NAME, event="uEvent")
    else:
        return redirect(url_for(f'/events/'))