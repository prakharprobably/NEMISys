from flask import Blueprint, render_template,request,redirect,url_for,flash
from werkzeug.utils import secure_filename
from .auth import protect, withName
from . import participantdbwrapper as partdb
from . import schooldbwrapper as schooldb
from . import exelwrapper as xl
import os

manage = Blueprint('manage', __name__)
@manage.route('/')
@protect(['EI','TC'])
@withName
def home(UUID,NAME):
    return render_template('partman/partman.html',uuid=UUID,name=NAME)


@manage.route('/viewparticipants')
@protect(['EI','TC'])
def view(UUID):
    print(f"ROUTER@{UUID}:access granted")
    data = partdb.getTable()
    return render_template("table.html",data=data)

@manage.route('/viewschools')
@protect(['EI','TC'])
def views(UUID):
    print(f"ROUTER@{UUID}:access granted")
    data = schooldb.getTable()
    return render_template("table.html",data=data)

@manage.route('/uploaddata', methods=['GET', 'POST'])
@protect(['EI', 'TC'])
def upload(UUID):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file.")
            return redirect(request.url)
        if file and file.filename.lower().endswith('.xlsx'):
            # Save the file as 'upload.xlsx' in the working directory
            filename = secure_filename('upload.xlsx')
            save_path = os.path.join(os.getcwd(), filename)
            file.save(save_path)
            try:
                print("parsing")
                schools, participants = xl.genTups(save_path)
            except Exception as e:
                print(f"Error parsing file: {e}")
                flash(f"Error parsing file: {e}")
                return redirect(request.url)
            finally:
                os.remove(save_path)
            for school in schools:
                try:
                    cur, con = schooldb.open()
                    schooldb.insert(cur, *school)
                    schooldb.confirm(con)
                    schooldb.close((cur, con))
                    print("inserted successfully")
                except Exception as e:
                    print(f"Failed to insert school: {e}")
                    flash(f"Failed to insert school: {e}")
            for participant in participants:
                try:
                    cur, con = partdb.open()
                    partdb.insertParticipant(cur, *participant)
                    partdb.confirm(con)
                    partdb.close((cur, con))
                    print("inserted successfully")
                except Exception as e:
                    print((f"Failed to insert participant: {e}"))
                    flash(f"Failed to insert participant: {e}")
            flash("File uploaded and processed successfully.")
            return redirect(url_for('manage.upload'))
        else:
            flash("Invalid file type. Only .xlsx files are accepted.")
            return redirect(request.url)

    return render_template('partman/upload.html')

@manage.route('/modparticipant', methods=['GET', 'POST'])
@protect(['EI', 'TC'])
def modifyparticipant(pid):
    oldData = None
    try:
        partcurcon = partdb.open()
        if request.method == 'GET':
            uuid = request.args.get('uuid')
            if uuid:
                oldData = staffdb.getData(cur=staff[0], uuid=uuid)
                if not oldData:
                    flash(f"No user found with UUID {uuid}")
        else:
            uuid = request.form.get('uuid')
            oldData = staffdb.getData(cur=staff[0], uuid=uuid)
            if not oldData:
                flash(f"No user found with UUID {uuid}")
                return render_template("modify.html", oldData=None)
            tokens = tokendb.open()
            name = request.form.get('name') or None
            cls = request.form.get('class') or None
            section = request.form.get('section') or None
            event = request.form.get('event') or None
            permissions = request.form.getlist('permissions') or None
            staffdb.modUser(cur=staff[0], uuid=uuid, name=name, cls=cls, section=section, event=event, perms=permissions)
            tokendb.modTokenPerms(cur=tokens[0],uuid=uuid,perms=permissions,event=event)
            staffdb.confirm(staff[1])
            tokendb.confirm(tokens[1])
            tokendb.close(tokens)
            print(f"ADMIN.MODIFY@{UUID}: Modified user {uuid}")
            flash(f"Updated user {uuid} successfully.")
            oldData = staffdb.getData(cur=staff[0], uuid=uuid)
    except Exception as e:
        print(f"\nADMIN.MODIFY@{UUID}: Something went wrong\ninput={request.form}\n{e}\n")
        flash("An error occurred during the operation.")
    finally:
        staffdb.close(staff)
        return render_template("admin/modify.html", oldData=oldData)

