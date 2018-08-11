from flask import Flask
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
#创建app实例
app=Flask(__name__)



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
app.config.from_object(Config)
# SQLAlchemy(app)

db=SQLAlchemy(app)
#配置redis
myredis=StrictRedis(host=Config.redisip,port=Config.redisport)


@app.route('/')
def index():
    myredis.set('name','wang')
    return 'index'

if __name__ == '__main__':

    app.run()

