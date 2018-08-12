from flask import session
from info import myredis
from . import blue_index
#创建路由
@blue_index.route('/',methods=['get','post'])
def index():
    session['userid']=111
    import  logging
    logging.debug('测Debug')
    # 没有自动提示(需要指定myredis类型)
    myredis.set('name','wang')

    return 'redisindex'