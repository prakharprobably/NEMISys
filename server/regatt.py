from flask import Blueprint, render_template,request,redirect,url_for,flash
from .auth import protect, withName
from .attendancedbwrapper import getBySchool, markPresent, open, confirm, close
from .schooldbwrapper import getTranslation

regatt = Blueprint('regatt', __name__)
@regatt.route('/', methods = ['GET','POST'])
@protect(['EI','TC','RG'])
@withName
def home(UUID,NAME):
    translation = getTranslation()
    snames = list(translation.keys())
    if request.method == 'POST':
        sname = request.form['sname']
        try:
            sid =  translation[sname]
        except:
            sid = None
        return redirect(url_for('regatt.attendance', sid=sid))
    return render_template('regattendance.html', uuid=UUID, name=NAME, snames=snames)

@regatt.route('/attendance', methods = ['GET', 'POST'])
@protect(['EI','TC','RG'])
def attendance(UUID):
    if request.method == 'GET':
        sid = request.args.get('sid')
        if not sid:
            return "No SID provided", 400
        data = getBySchool(sid)
        return render_template('attendance.html', data=data)
    if request.method == 'POST':
        cur, conn = open()
        sid = request.args.get('sid')
        if not sid:
            return "No SID provided", 400
    
        data = getBySchool(sid)
        all_ids = {row[0] for row in data[1:]}  # skip header
        checked_ids = {int(key.split('_')[1]) for key in request.form if key.startswith('attendance_')}
        unchecked_ids = all_ids - checked_ids
    
        for pid in checked_ids:
            markPresent(cur, pid, True)
        for pid in unchecked_ids:
            markPresent(cur, pid, False)
    
        confirm(conn)
        close((cur, conn))
        print("successfully marked the attendance")
        data = getBySchool(sid)
        return render_template('attendance.html', data=data)
    return "something messed up"