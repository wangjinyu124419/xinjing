from flask import current_app
from flask import render_template
from flask import session
from info import myredis
from . import blue_index
#创建路由
@blue_index.route('/')
def index():

    return render_template('news/index.html')


@blue_index.route('/favicon.ico')
def favicon():
    #这里追踪下源码,不太清楚
    return current_app.send_static_file('news/favicon.ico')
