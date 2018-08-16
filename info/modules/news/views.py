import logging

from flask import abort
from flask import session, jsonify

from info import constants, db
from info import response_code
from info.models import User,  News
from . import blue_news
from flask import render_template

@blue_news.route('/detail/<int:news_id>')
def news_detail(news_id):

    #1.查询用户信息
    user_id=session.get('user_id',None)
    user=None
    if user_id:
        try:
            user=User.query.get(user_id)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户失败')

    #2.查询点击排行
    news_clicks=None
    try:
        news_clicks=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻排行失败')


    #3.查询新闻详情信息
    news_detail=None
    try:
        news_detail=News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        #抛出404,将来对404统一处理
    if not news_detail:
        abort(404)
    news_detail.clicks+=1
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()

    #4.查看收藏状态
    if not user:
        is_colletted = False
    else:

        if news_detail in user.collection_news:
            is_colletted = True
    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news_detail':news_detail.to_dict(),
        'is_colletted':is_colletted,
    }

    return render_template('news/detail.html',context=context)
