from flask import Blueprint, render_template,request,redirect,url_for,flash
from .auth import protect, withName
from .attendancedbwrapper import getBySchool, markPresent, open, confirm, close
from . import attendancedbwrapper as attdb
from . import participantdbwrapper as partdb
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
        for row in data[1:]:  # skip header
            pid = row[0]
            updated = {}
            # Compare submitted fields with existing values
            submitted_name = request.form.get(f'name_{pid}')
            if submitted_name != row[1]:
                updated['name'] = submitted_name
            submitted_class = request.form.get(f'class_{pid}')
            if str(submitted_class) != str(row[2]):
                updated['clss'] = submitted_class
            submitted_sid = request.form.get(f'sid_{pid}')
            if updated:
                partdb.modPart(cur, pid, **updated)
                attdb.modPart(cur,pid, **updated)
                print(updated)
            attendance = pid in checked_ids
            markPresent(cur, pid, attendance)
        conn.commit()
        confirm(conn)
        close((cur, conn))
        print("successfully updated attendance and participant data")
        data = getBySchool(sid)
        return render_template('attendance.html', data=data)
