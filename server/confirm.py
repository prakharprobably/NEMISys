from flask import Blueprint, render_template, request
from .auth import protect, withName
from .participantdbwrapper import open, seperateIntoEvents, close, revert

confirm = Blueprint('confirm', __name__)

@confirm.route('/', methods = ['GET','POST'])
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    print(UUID)
    event = request.form.get('trigger')
    print("confirming")
    if event=='conRegs':
        cur,conn = open()
        seperateIntoEvents((cur,conn))
        close((cur,conn))
    elif event=='comVirts':
        pass
    elif event=='comRes':
        pass
    print(event)
    return render_template("confirm.html",uuid=UUID, name=NAME)

@confirm.route('/revert', methods = ['GET', 'POST'])
@protect(['EI','TC'])
@withName
def rollback(UUID, NAME):
    event = request.form.get('revert')
    print("rolling back")
    if event=='rollback':
        cur,conn= open()
        revert((cur,conn))
        close((cur,conn))
    return render_template("confirm.html",uuid=UUID, name=NAME)