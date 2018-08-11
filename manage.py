from info import  createapp,db
from flask import  session
from flask_script import  Manager
from flask_migrate import MigrateCommand,Migrate

import os,base64
app=createapp('dev')
print('我的app',app)

mymanager=Manager(app)
#让迁移时数据库和app关联
Migrate(app,db)
#
#迁移脚本命令添加到脚本管理对象

mymanager.add_command('dbnickname',MigrateCommand)

@app.route('/',methods=['get','post'])
def index():
    session['userid']=111
    import  logging
    logging.debug('测Debug')
    # myredis.set('name','wang')
    return 'index'

if __name__ == '__main__':

    # app.run()
    mymanager.run()

