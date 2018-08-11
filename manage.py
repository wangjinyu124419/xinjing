from flask import Flask
from redis import StrictRedis
from flask_sqlalchemy import SQLAlchemy
#创建app实例
app=Flask(__name__)

db=SQLAlchemy(app)

# app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:mysql@127.0.0.1:3306/flaskdb"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#配置app
class Config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/flaskdb_1"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

app.config.from_object(Config)


@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    pass
    app.run()

