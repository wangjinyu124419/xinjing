from flask import Flask
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import  Session
from flask import  session
from flask_script import  Manager
from flask_migrate import MigrateCommand,Migrate

import os,base64


#创建app实例
app=Flask(__name__)

#生成秘钥
# print(base64.b64decode(os.urandom(48)))

# app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:mysql@127.0.0.1:3306/flaskdb"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#配置app
class Config(object):
    DEBUG=True
    # SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/flaskdb_1"
    # SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/flaskdb_1'
    # 禁用追踪mysql:因为mysql的性能差，如果再去追踪mysql的所有的修改，会再次浪费性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    redisip='127.0.0.1'
    redisport=6379
    SECRET_KEY  = '123'
    #配置大写Session
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host=redisip,port=redisport)
    # SESSION_USE_SIGNER=True
    PERMANENT_SESSION_LIFETIME=24*60*60

app.config.from_object(Config)
# SQLAlchemy(app)

db=SQLAlchemy(app)
#配置redis
myredis=StrictRedis(host=Config.redisip,port=Config.redisport)

#配置csrf

CSRFProtect(app)
Session(app)
mymanager=Manager(app)
#让迁移时数据库和app关联
Migrate(app,db)
#迁移脚本命令添加到脚本管理对象

mymanager.add_command('dbnickname',MigrateCommand)

@app.route('/',methods=['get','post'])
def index():
    session['userid']=111
    # myredis.set('name','wang')
    return 'index'

if __name__ == '__main__':

    # app.run()
    mymanager.run()

