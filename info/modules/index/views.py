import logging
from flask import current_app, jsonify
from flask import render_template
from flask import session

from info import constants
from info import myredis
from info import response_code

from info.models import User, News
from . import blue_index
#创建路由
@blue_index.route('/')
def index():
    #1.session中读取用户登陆信息

    user_id=session.get('user_id',None)
    #2.查询redis里的用户信息


    user=None
    if user_id:
        try:
            user=User.query.get(user_id)
        except Exception as e:
            logging.error(e)
            # return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户失败')


    #3.查询新闻排行
    news_clicks=None
    try:
        news_clicks=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻排行失败')
    # 构造渲染数据模板
    context={
        'user':user.to_dict() if user else None,
        'news_clicks':news_clicks,
    }
    # 响应渲染后的主页
    return render_template('news/index.html',context=context)


@blue_index.route('/favicon.ico')
def favicon():
    #这里追踪下源码,不太清楚
    return current_app.send_static_file('news/favicon.ico')
