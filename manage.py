from info import  createapp,db,models
from flask import  session
from flask_script import  Manager
from flask_migrate import MigrateCommand,Migrate
import os,base64

from info.models import User

app=createapp('dev')

mymanager=Manager(app)
#让迁移时数据库和app关联
Migrate(app,db)
#https://gitee.com/wangjinyu124419/myflask-1.git
#迁移脚本命令添加到脚本管理对象

mymanager.add_command('dbnickname',MigrateCommand)

# @app.route('/',methods=['get','post'])
# def index():
#     session['userid']=111
#     import  logging
#     logging.debug('测Debug')
#     # myredis.set('name','wang')
#     return 'index'


# 以下代码是自定义脚本
@mymanager.option('-u', '-username', dest='username')
@mymanager.option('-p', '-password', dest='password')
@mymanager.option('-m', '-mobile', dest='mobile')
def createsuperuser(username, password, mobile):
    """
    创建管理员的函数
    :param name: 管理员名字
    :param password: 管理员密码
    """
    if not all([username,password,mobile]):
        print('缺少参数')
    else:
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        user.is_admin = True # 核心代码（管理员的本质）
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)

if __name__ == '__main__':
    print(app.url_map)
    # app.run()
    mymanager.run()

