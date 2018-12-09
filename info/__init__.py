import logging
from logging.handlers import RotatingFileHandler
# from info.utils.comment import do_rank

from flask import Flask
from flask import g
from flask import render_template
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect,csrf
from flask_session import  Session
from config import Config,dictconfig
import pymysql
pymysql.install_as_MySQLdb()

db=SQLAlchemy()
myredis=None #type:# StrictRedis
def set_log(level):
    # 设置日志的记录等级。
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
def createapp(config_name):
    config_class=dictconfig[config_name]
    set_log(config_class.loglevel)
    #创建app实例
    app=Flask(__name__)
    #生成秘钥
    # print(base64.b64decode(os.urandom(48)))

    app.config.from_object(config_class)
    # SQLAlchemy(app)
    global db
    # db=SQLAlchemy(app)
    db.init_app(app)
    #配置redis
    global myredis
    myredis=StrictRedis(host=config_class.redisip,port=config_class.redisport,decode_responses=True)

    #配置csrf

    CSRFProtect(app)
    Session(app)
    #注册蓝图
    from info.modules.index import blue_index
    app.register_blueprint(blue_index)
    from info.modules.passport import blue_passport
    app.register_blueprint(blue_passport)
    from info.modules.news import blue_news
    app.register_blueprint(blue_news)
    from info.modules.user import blue_user
    app.register_blueprint(blue_user)
    from info.modules.admin import blue_admin
    app.register_blueprint(blue_admin)


    #如果导入do_rank 则无法导入db的bug
    from info.utils.comment import do_rank
    #添加自定义过滤器到过滤器模板列表
    app.add_template_filter(do_rank,'rank')


    #每次响应是写入一个cookie,csrf_token
    @app.after_request
    def set_crsf_token(response):
        # generate_csrf()生成一个签名的csrf_token,同时保存到session
        csrf_token=csrf.generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        # print('生成的token:',csrf_token)
        return response

    from info.utils.comment import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_notfound(e):
        context={'user':g.user.to_dict() if g.user else None}
        return render_template('news/404.html',context=context)
    return  app