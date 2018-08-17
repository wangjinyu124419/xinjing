import logging
from flask import abort
from flask import g
from flask import request
from flask import session, jsonify
from info import constants, db
from info import response_code
from info.models import User,  News,Comment
from info.utils.comment import user_login_data
from . import blue_news
from flask import render_template

#新闻评论
@blue_news.route('/news_comment',methods=['POST'])
@user_login_data
def news_comment():
    #1.判断是否登陆
    user=g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    #2.接受参数,news_id,comment,parent_id
    json_dict=request.json
    news_id=json_dict.get('news_id')
    comment=json_dict.get('comment')
    parent_id=json_dict.get('parent_id' )
    #3.校验参数齐全,判断news_id,parent_id是整数
    if not all([news_id,news_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不全')
    #4.根据news_id判断新闻是否存在
    try:
        news_id=int(news_id)
        #如果没有parent_id,就表示评论新闻,传入表示评论别人回复
        if parent_id:
            parent_id=int(parent_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数不是整数')

    try:
        news=News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.DBERR, errmsg='新闻不存在')
    #5.创建comment模型
    comment_obj=Comment()

    comment_obj.content = comment
    comment_obj.user_id=user.id
    comment_obj.news_id=news.id
    if parent_id:
        comment_obj.parent_id=parent_id

    # 6.同步到数据库
    try:
        db.session.add(comment_obj)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存数据失败')


    #7.响应评论结果,讲评论数据返回前端渲染
    return jsonify(errno=response_code.RET.OK, errmsg='评论成功',data=comment_obj.to_dict())


@blue_news.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    #0.判断用户是否登陆
    user=g.user
    if not user:
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户失败')

    #1.接受参数,action,news_id
    json_dict=request.json
    news_id=json_dict.get('news_id')
    action=json_dict.get('action')

    #2.校验参数齐全, 判断action是否是'collect', 或者'cancel_collect'
    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少必传参数')
    # 3.判断新闻是否存在news_id
    try:
        news=News.query.get(news_id)
    except  Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.DBERR, errmsg='新闻不存在')

    # 4.根据action收藏或者取消收藏
    if action=='collect':
        #收藏
        if news not in user.collection_news:
            user.collection_news.append(news)

    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
        # 取消收藏
    #5.同步数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.OK, errmsg='存储数据失败')
    return jsonify(errno=response_code.RET.OK, errmsg='收藏或取消收藏成功')

        #5.返回收藏结果


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

    is_colletted = False
    if  user:
        if news_detail in user.collection_news:
            is_colletted = True
    #5.查询评论信息前端渲染
    comments=None
    try:
        comments=Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻评论失败')
    # if not comments:
    #     return jsonify(errno=response_code.RET.DBERR, errmsg='无新闻评论')
    comment_dict_list=[]
    for comment in comments:
        comment.to_dict()
        comment_dict_list.append(comment.to_dict() )

    context = {
        'user': user.to_dict() if user else None,
        'news_clicks': news_clicks,
        'news_detail':news_detail.to_dict(),
        'is_colletted':is_colletted,
        'comments':comment_dict_list

    }
    # context = {
    #     'user': user.to_dict() if user else None,
    #     'news_clicks': news_clicks,
    #     'news': news.to_dict(),
    #     'is_collected': is_collected,
    #     'comments': comment_dict_list
    # }

    return render_template('news/detail.html',context=context)
