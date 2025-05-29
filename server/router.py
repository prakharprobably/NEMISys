from flask import Blueprint, render_template,request,redirect,url_for
from . import staffdbwrapper as staffdb
from .auth import protect, withName

routes= Blueprint('routes', __name__)

@routes.route('/')
@protect(["EI"])
@withName
def home(UUID, NAME):
    return render_template("base.html",uuid=UUID,name=NAME,body="You are allowed to access this page")

    #token = request.cookies.get("token")
    #print(f"ROUTER: attempted access with {token}")
    #try:
    #    PERMS = tokens[token][1]
    #    UUID = tokens.get(token)[0]
    #    if "EI" not in PERMS:
    #        print(f"ROUTER@{UUID}: Access denied")
    #        return f"{UUID} is not allowed to access this page"
    #    else:
    #        print(f"ROUTER@{UUID}:access granted")
    #        return f"{UUID} is allowed to access this page"
    #except:
    #    print("ROUTER: redirected to login")
    #    return redirect(url_for("auth.login"))
    

