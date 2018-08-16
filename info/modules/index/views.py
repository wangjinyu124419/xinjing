import logging
from flask import current_app, jsonify
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import myredis
from info import response_code

from info.models import User, News,Category
from . import blue_index

@blue_index.route('/news_list')
def index_news_list():
    #1.接受参数,新闻分类id,当前页,每页多少数据
    cid=request.args.get('cid','1')
    page=request.args.get('page','1')
    per_page=request.args.get('per_page','5')

    #2,校验参数,参数是否齐全,参数是否都为整数
    if not all(['cid','page','per_page']):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数信息不全')

    try:
        cid=int(cid)
        page=int(page)
        per_page=int(per_page)
    except Exception as e:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='请传入整数')

    #3,进行分页查询,
    try:
        if cid==1:
            paginates=News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
        else:
            paginates=News.query.filter(News.category_id==cid).paginate(page,per_page,False)
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询分类新闻失败')
    #4,构造响应数据
    total_pages=paginates.pages
    current_page=paginates.page
    news_list=paginates.items
    news_dict_list=[]
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    #5,返回响应数据
    return jsonify(errno=response_code.RET.OK, errmsg='OK',cid=cid,current_page=current_page,total_pages=total_pages,news_dict_list=news_dict_list)


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
    try:
        news_categories=Category.query.all()
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻分类失败')

    # 构造渲染数据模板
    context={
        'user':user.to_dict() if user else None,
        'news_clicks':news_clicks,
        'news_categories':news_categories
    }
    # 响应渲染后的主页
    return render_template('news/index.html',context=context)


@blue_index.route('/favicon.ico')
def favicon():
    #这里追踪下源码,不太清楚
    return current_app.send_static_file('news/favicon.ico')
