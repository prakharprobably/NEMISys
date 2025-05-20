from flask import Blueprint, render_template,request,redirect,url_for
from . import staffdbwrapper as staffdb
from .auth import protect, withName

routes= Blueprint('routes', __name__)

@routes.route('/')
@protect(["EI"])
@withName
def home(UUID, NAME):
    return render_template("base.html",uuid=UUID,name=NAME,body="You are allowed to access this page")
