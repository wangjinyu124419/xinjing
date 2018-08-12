from flask import Blueprint

#创建蓝图
blue_index=Blueprint('index',__name__)

#导入视图
from . import views

