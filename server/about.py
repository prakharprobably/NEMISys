from flask import Blueprint, render_template,request,redirect,url_for,flash
from .auth import protect, withName

about= Blueprint('about', __name__)
@about.route('/')
@protect(['EI','TC'])
@withName
def home(UUID, NAME):
    return render_template('about.html', uuid=UUID, name=NAME)