from flask import Blueprint
blue_admin=Blueprint('admin',__name__,url_prefix='/admin')
from . import views

