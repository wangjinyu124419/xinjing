from functools import wraps

from flask import g


def do_rank(myindex):
    if myindex==1:
        return 'first'
    elif myindex==2:
        return 'second'
    elif myindex==3:
        return 'third'
    else:
        return ''
# 如果提前导入do_rank
# 这段代码无法运行
import logging
from flask import session
from info.models import User
#
# def get_use_info():
#     user_id=session.get('user_id',None)
#     user=None
#     if user_id:
#         try:
#             user=User.query.get(user_id)
#         except Exception as e:
#             logging.error(e)
#     return user

def user_login_data(view_func):
    # 不让装饰器修改被装饰的视图函数的__name__属性，防止路由出错
    @wraps(view_func)
    #获取用户信息装饰器
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id', None)
        user=None
        if user_id:
            try:
                user=User.query.get(user_id)
            except Exception as e:
                logging.error(e)
                # 使用g变量存储查询到的用户的基本信息
                # g变量时应用上下文，只在当前的请求中有效，不同的请求中，各自的g变量不同
                # g.user 表示定义上文，下文可以在视图函数中读取，因为进入到装饰器的请求和视图函数的请求时同一个请求
        g.user=user
        return view_func(*args,**kwargs)

    return    wrapper
