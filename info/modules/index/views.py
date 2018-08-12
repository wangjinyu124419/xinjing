from flask import render_template
from flask import session
from info import myredis
from . import blue_index
#创建路由
@blue_index.route('/',methods=['get','post'])
def index():


    return render_template('news/index.html')