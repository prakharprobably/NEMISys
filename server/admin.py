from flask import Blueprint, render_template,request,redirect,url_for,flash
from .auth import protect, withName
from . import authdbwrapper as authdb
from . import staffdbwrapper as staffdb
from . import tokendbwrapper as tokendb

admin= Blueprint('admin', __name__)
@admin.route('/')
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    return render_template("admin/admin.html",uuid=UUID,name=NAME)


@admin.route('/view')
@protect(['EI','TC'])
def view(UUID):
    print(f"ROUTER@{UUID}:access granted")
    staff=staffdb.open()
    data=staffdb.getTable(staff[0])
    staffdb.close(staff)
    return render_template("table.html",data=data)


@admin.route('/insert',methods=['GET','POST'])
@protect(['EI','TC'])
def insert(UUID):
    print(f"ADMIN.INSERT@{UUID}: Access granted")
    uuid=request.form.get('uuid')
    passkey = request.form.get('passkey')
    name = request.form.get('name')
    cls = request.form.get('class')
    section = request.form.get('section')
    event = request.form.get('event')
    permissions = request.form.getlist('permissions')
    staff = staffdb.open()
    oauth = authdb.open()
    try:
        staffdb.insertUser(cur=staff[0], uuid=uuid, name=name, cls=cls, section=section, event=event, perms=permissions)
        authdb.insertUser(cur=oauth[0], uuid=uuid, passkey=passkey)
        authdb.confirm(oauth[1])
        staffdb.confirm(staff[1])
        print(f"ADMIN.INSERT@{UUID}: Added user {uuid}")
        flash("added user")
    except Exception as e:
        print(f"\nADMIN.INSERT@{UUID}: Something went wrong\nform={request.form}\n{e}\n")
        flash("something went wrong")
    staffdb.close(staff)
    authdb.close(oauth)
    return render_template("admin/insert.html")

@admin.route('/modify', methods=['GET', 'POST'])
@protect(['EI', 'TC'])
def modify(UUID):
    oldData = None
    try:
        staff = staffdb.open()
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

@admin.route('/remove',methods=['GET','POST'])
@protect(['EI','TC'])
def remove(UUID):
    try:
        uuid=request.form.get('uuid')
        staff = staffdb.open()
        oauth = authdb.open()
        tokens = tokendb.open() 
        staffdb.deleteUser(cur=staff[0], uuid=uuid)
        authdb.deleteUser(cur=oauth[0], uuid=uuid)
        tokendb.clean(cur=tokens[0], uuid=uuid)
        staffdb.confirm(staff[1])
        authdb.confirm(oauth[1])
        tokendb.confirm(tokens[1])
        print(f"ADMIN.REMOVE@{UUID}: Removed user {uuid}")
    except Exception as e:
        print(f"\nADMIN.REMOVE@{UUID}:Something went wrong\ninput={request.form}\n{e}\n")
    staffdb.close(staff)
    authdb.close(oauth)
    return render_template("admin/remove.html")

@admin.route('/resetpassword',methods=['GET','POST'])
@protect(['EI','TC'])
def resetpassword(UUID):
    try:
        uuid=request.form.get('uuid')
        passkey = request.form.get('passkey')
        oauth = authdb.open()
        authdb.modUser(cur=oauth[0],uuid=uuid,passkey=passkey)
        authdb.confirm(oauth[1])
        print(f"ADMIN.RESETPASS@{UUID}: Password changed for {uuid}")
    except Exception as e:
        print(f"\nADMIN.RESETPASS@{UUID}: Something went wrong\ninput={request.form}\n{e}\n")
    authdb.close(oauth)
    return render_template("admin/changepass.html")
