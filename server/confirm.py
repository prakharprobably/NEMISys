from flask import Blueprint, render_template, request
from .auth import protect, withName
from .participantdbwrapper import open, seperateIntoEvents, close, revert, seperatePregrads
from .attendancedbwrapper import inherit, init
from . import eventdbwrapper as evdb
from . import resultsdbwrapper as resdb
from . import certsdbwrapper as certdb

confirm = Blueprint('confirm', __name__)

@confirm.route('/', methods = ['GET','POST'])
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    print(UUID)
    event = request.form.get('trigger')
    if event=='comRegs':
        init()
        inherit()
    elif event=='conRegs':
        cur,conn = open()
        seperateIntoEvents((cur,conn))
        conn.commit()
        close((cur,conn))
    elif event=='comVirt':
        cur,conn = open()
        evdb.genAtt((cur,conn), event="Virtual Warriors", round="prelims")
        conn.commit()
        cur.close()
        conn.close()
    elif event=='comOnlP':
        cur,conn=open()
        seperatePregrads((cur,conn))
        conn.commit()
        cur.close()
        conn.close()
    elif event=='comRes':
        resdb.init()
    elif event=='conRes':
        certdb.genMerits()
        certdb.genParts()
        certdb.genAppr()
    print(event)
    return render_template("confirm.html",uuid=UUID, name=NAME)

@confirm.route('/revert', methods = ['GET', 'POST'])
@protect(['EI','TC'])
@withName
def rollback(UUID, NAME):
    event = request.form.get('revert')
    if event=='rollback':
        cur,conn= open()
        revert((cur,conn))
        close((cur,conn))
    print(event)
    return render_template("confirm.html",uuid=UUID, name=NAME)