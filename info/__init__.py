import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import  Session
from config import Config,dictconfig

db=SQLAlchemy()
def set_log(level):
    # 设置日志的记录等级。
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("/home/python/PycharmProjects/flask项目-1/myflask_1/logs/log", maxBytes=1024*1024*100, backupCount=10)
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
    myredis=StrictRedis(host=config_class.redisip,port=config_class.redisport)

    #配置csrf

    CSRFProtect(app)
    Session(app)
    return  app