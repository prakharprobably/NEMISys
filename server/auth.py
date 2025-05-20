from flask import Blueprint, render_template, flash, make_response, request,redirect,url_for
from functools import wraps
from . import authdbwrapper as authdb
from . import staffdbwrapper as staffdb
from . import tokendbwrapper as tokendb
import secrets
import hashlib

def genToken(uuid,staff):
    raw = secrets.token_bytes(32)
    token = hashlib.sha256(raw).hexdigest()
    tokens = tokendb.open()
    staff=staffdb.open()
    tokendb.create(cur=tokens[0], token=token, uuid=uuid, event=staffdb.getEvent(cur=staff[0], uuid=uuid), perms=staffdb.getPerms(cur=staff[0], uuid=uuid))
    tokendb.confirm(tokens[1])
    tokendb.close(tokens)
    staffdb.close(staff)
    return token


def protect(reqPerms):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            token = request.cookies.get("token")
            print(f"{func.__name__.upper()}: attempted access with {token}")
            tokens = tokendb.open()
            if tokendb.checkToken(cur=tokens[0],token=token):
                UUID = tokendb.getTokenUUID(cur=tokens[0], token=token)
                staff = staffdb.open()
                NAME = staffdb.getName(cur=staff[0],uuid=UUID)
                staffdb.close(staff)
                PERMS = tokendb.getTokenPerms(cur=tokens[0], token=token)
                tokendb.update(cur=tokens[0], token=token)
                tokendb.confirm(tokens[1])
                tokendb.close(tokens)
                if any(perm in PERMS for perm in reqPerms):
                    print(f"{func.__name__.upper()}@{UUID}: Access granted")
                    return func(*args, UUID=UUID, **kwargs)
                else:
                    print(f"{func.__name__.upper()}@{UUID}: Access denied")
                    return make_response(render_template("401.html", body=f"{UUID} is unauthorized", uuid=UUID, name=NAME), 401)
            else:
                tokendb.close(tokens)
                print(f"{func.__name__.upper()}: redirected to login.")
                return redirect(url_for("auth.login"))
        return decorated_function
    return decorator

def withName(func):
    @wraps(func)
    def wrapper(*args, UUID=None, **kwargs):
        if UUID is None:
            raise ValueError("UUID not provided to with_name decorator")
        staff = staffdb.open()
        try:
            NAME = staffdb.getName(staff[0], uuid=UUID)
        except:
            NAME = None
        staffdb.close(staff)
        return func(*args, UUID=UUID, NAME=NAME, **kwargs)
    return wrapper

auth =  Blueprint("auth", __name__)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    token = request.cookies.get("token")
    tokens = tokendb.open()
    if tokendb.checkToken(cur=tokens[0],token=token):
        tokendb.close(tokens)
        return redirect(url_for("auth.logout"))
    tokendb.close(tokens)
    UUID=request.form.get('uuid')
    passkey = request.form.get('passkey')
    staff = staffdb.open()
    oauth = authdb.open()
    try:
        if authdb.checkLogin(oauth[0], UUID, passkey):
            print(f"AUTH: Successful login to {UUID}")
            token = genToken(UUID,staff[0])
            flash("successful login", category="success")
            resp = make_response(redirect(url_for("routes.home")))
            resp.set_cookie('token', token, httponly=True, samesite='Strict')
            return resp
        else:
            print(f"AUTH: Attempted login to {UUID}")
            flash("incorrect credentials",category="failure")
            return render_template("login.html")
    finally:
        staffdb.close(staff)
        authdb.close(oauth)

@auth.route('/logout', methods=['GET','POST'])
def logout():
    token = request.cookies.get("token")
    print(f"AUTH.LOGOUT: attempted logout with {token}")
    tokens = tokendb.open()
    if tokendb.checkToken(cur=tokens[0],token=token):
        UUID = tokendb.getTokenUUID(cur=tokens[0], token=token)
        tokendb.clean(cur=tokens[0], token=token)
        tokendb.confirm(conn=tokens[1])
        print(f"AUTH.LOGOUT@{UUID}: {token} destroyed")
    tokendb.close(tokens)
    return redirect(url_for("auth.login"))