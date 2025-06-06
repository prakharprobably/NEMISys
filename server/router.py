from flask import Blueprint, render_template,request,redirect,url_for
from . import staffdbwrapper as staffdb
from .auth import protect, withName
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

routes= Blueprint('routes', __name__)

@routes.route('/')
@protect(["TC", "EI", "SI", "CW", "RC", "RG"])
@withName
def home(UUID, NAME):
    cur,conn = staffdb.open()
    perms = staffdb.getPerms(cur, UUID)
    staffdb.close((cur,conn))
    if "TC" in perms or "EI" in perms:
        events = creds["Events"]
        event = request.form.get('event')
        if event:
            return redirect('/events/{event}')
        else:
            return render_template("home.html", uuid=UUID, name=NAME, events=events)
    elif "SI" in perms:
        return redirect(url_for('events.redir'))
    elif "RC" in perms:
        return redirect(url_for('results.home'))
    elif "CW" in perms:
        return redirect(url_for('certs.home'))
    elif "RG" in perms:
        return redirect(url_for('regatt.home'))
    else:
        return render_template("base.html",uuid=UUID,name=NAME,body="You are allowed to access this page")
    

