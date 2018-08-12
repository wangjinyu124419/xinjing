from flask import session

from . import blue_index
#创建路由
@blue_index.route('/',methods=['get','post'])
def index():
    session['userid']=111
    import  logging
    logging.debug('测Debug')
    # myredis.set('name','wang')
    return 'index'