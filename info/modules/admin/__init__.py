from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import url_for

blue_admin=Blueprint('admin',__name__,url_prefix='/admin')
from . import views

# 以下代码是对非管理员用户进入后台站点的权限的限制
@blue_admin.before_request
def admin_authentication():
    """管理员的认证
    1.如果当前的用户是非管理员用户，当访问登录界面时，直接将登录界面响应给他
    2.如果当前的用户是非管理员用户，当访问非登录界面时，直接将其引导到前台的主页 （需要实现的）
    3.注意：以上的两个认证，是后台的每个请求都要去执行的
    """
    # 用户访问的是非登录界面
    if not request.url.endswith('/admin/login'):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin')

        # 将用户引导到前台的主页
        if not user_id or not is_admin:
            return redirect(url_for('index.index'))