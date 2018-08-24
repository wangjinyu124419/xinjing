import datetime
import logging

import time

from flask import abort, jsonify
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info import constants, db
from info import response_code
from info.models import User, News, Category
from info.utils.comment import user_login_data
from info.utils.file_storage import upload_file
from . import blue_admin


@blue_admin.route('/news_type',methods=['GET','POST'])
def news_type():
    if request.method=='GET':
        categories=Category.query.all()
        categories.pop(0)
        context={
            'categories':categories,
        }
        return  render_template('admin/news_type.html',context=context)
    if request.method == 'POST':
        # 2.1 接受参数：cid, cname
        cid = request.json.get('id')
        cname = request.json.get('name')

        # 2.2 校验参数：cid是可选的参数，cname必传
        if not cname:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        # 2.3 根据cid判断，是新增分类还是修改分类（核心代码）
        if cid:
            # 修改分类
            try:
                category = Category.query.get(cid)
            except Exception as e:
                logging.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻分类失败')
            if not category:
                return jsonify(errno=response_code.RET.NODATA, errmsg='分类不存在')

            # 将传入的cname，重新的赋值给category的name属性
            category.name = cname
        else:
            # 新增分类
            category = Category()
            category.name = cname
            db.session.add(category)

        # 2.4 同步到数据
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DATAERR, errmsg='更新数据失败')

        # 2.5 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='更新数据成功')



@blue_admin.route('/news_edit_detail/<int:news_id>',methods=['POST','GET'])
def news_edit_detail(news_id):
    if request.method=='GET':
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            abort(404)
        if not news:
            abort(404)
        categories=Category.query.all()
        categories.pop(0)
        context = {
            'news': news.to_dict(),
            'categories':categories,

        }
        return render_template('admin/news_edit_detail.html',context=context)
    if request.method=='POST':
        title=request.form.get('title')
        category_id=request.form.get('category_id')
        digest=request.form.get('digest')
        index_image=request.form.get('index_image')
        content=request.form.get('content')
        # 2.2 校验参数
        if not all([title, digest, content, category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

        try:
            news = News.query.get(news_id)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='查询新闻数据失败')

        if not news:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='新闻不存在')

        if index_image:
            try:
                index_image_data = index_image.read()
            except Exception as e:
                logging.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='图片参数错误')

            try:
                key = upload_file(index_image_data)
            except Exception as e:
                logging.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传图片到七牛云失败')

            # 需要将key修改
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key


        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存数据失败')

        # 2.5 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='OK')





@blue_admin.route('/news_edit')
def news_edit():
    """新闻板式编辑列表"""

    # 接受参数
    page = request.args.get('p', 1)

    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1

    # 分页查询：查询待审核的 (核心代码)
    news_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = News.query.filter(News.status == 0).order_by(
                News.create_time.desc()).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        logging.error(e)
        abort(404)

    # 构造渲染数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    # 响应结果
    return render_template('admin/news_edit.html', context=context)


@blue_admin.route('/news_review_action',methods=['POST'])
def news_review_action():
    news_id=request.json.get('news_id')
    action=request.json.get('action')
    if not all(['news_id','action']):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数不全')
    if action not  in ['accept','reject']:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')
    try:
        news=News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='查询失败失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA,errmsg='新闻不存在')

    if action=='accept':
        news.status=0
    else:
        reason=request.json.get('reason')
        if not reason:
            return jsonify(errno=response_code.RET.NODATA, errmsg='缺少拒绝原因')
        news.status=-1
        news.reason=reason
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='保存审核信息失败')
    return jsonify(errno=response_code.RET.OK, errmsg='OK')


@blue_admin.route('/news_review_detail/<int:news_id>')
@user_login_data
def news_review_detail(news_id):
    news=None
    try:
        news=News.query.get(news_id)
    except Exception as e:
        abort(404)
    if not news:
        abort(404)
    context={
        'news':news.to_dict()

    }


    return render_template('admin/news_review_detail.html',context=context)

@blue_admin.route('/news_review')
@user_login_data
def news_review():
    if request.method=='GET':
        page = request.args.get('p', 1)
        keyword= request.args.get('keyword')
        # 2.校验参数

        try:
            page = int(page)
        except Exception as e:
            logging.error(e)
            page = 1

        # 3.分页查询(核心代码)
        news = []
        total_page = 1
        current_page = 1
        if not keyword:
            try:
                paginate = News.query.filter(News.status!=0).paginate(page, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
                news = paginate.items
                total_page = paginate.pages
                current_page = paginate.page
            except Exception as e:
                logging.error(e)

        else:
            try:
                paginate = News.query.filter(News.status!=0,News.title.contains(keyword)).paginate(page, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
                news = paginate.items
                total_page = paginate.pages
                current_page = paginate.page
            except Exception as e:
                logging.error(e)
        news_dict_list=[]
        for new in news:
            news_dict_list.append(new.to_review_dict())

        context={

            'total_page':total_page,
            'current_page':current_page,
            'news_dict_list':news_dict_list,
        }



        return render_template('admin/news_review.html',context=context)


@blue_admin.route('/user_list')
@user_login_data
def user_list():
    #1.接受参数
    page=request.args.get('p',1)
    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1

    # 3.分页查询(核心代码)
    users = []
    total_page = 1
    current_page = 1
    try:
        paginate = User.query.filter(User.is_admin == False).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        logging.error(e)

    # 4.构造渲染数据
    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())
    context={
        'users':users,
        'total_page':total_page,
        'current_page':current_page,
        'user_dict_list':user_dict_list,
    }


    return render_template('admin/user_list.html',context=context)


@blue_admin.route('/user_count')
@user_login_data
def user_count():
    #1.查询用户总数
    total_count=0
    mouth_count=0
    day_count=0
    try:
        total_count=User.query.filter(User.is_admin==False).count()
    except Exception as e:
        logging.error(e)
    # 2.查询月新增
    t = time.localtime()
    month_begin_str='%d-%02d-01'%(t.tm_year,t.tm_mon)

    month_begin_date=datetime.datetime.strptime(month_begin_str,'%Y-%m-%d')
    try:
        mouth_count=User.query.filter(User.is_admin==False,User.create_time>=month_begin_date).count()
    except Exception as e:
        logging.error(e)

    #3.日新增人数
    t=time.localtime()
    day_begin_str='%d-%02d-%02d'%(t.tm_year,t.tm_mon,t.tm_mday)
    day_begin_date=datetime.datetime.strptime(month_begin_str,'%Y-%m-%d')
    try:
        day_count=User.query.filter(User.is_admin==False,User.create_time>=day_begin_date).count()
    except Exception as e:
        logging.error(e)
    active_date=[]
    active_count=[]

    today_begin='%d-%02d-%02d'%(t.tm_year,t.tm_mon,t.tm_mday)
    today_begin_date=datetime.datetime.strptime(today_begin,'%Y-%m-%d')
    for i in range(15):
        begin_date=today_begin_date-datetime.timedelta(days=(i))

        end_date=today_begin_date-datetime.timedelta(days=(i-1))

        count=User.query.filter(User.is_admin==False, User.last_login>=begin_date, User.last_login<end_date).count()
        # active_data.append(begin_date.strftime(begin_date,'%Y-%m-%d')).reverse()
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))
        active_count.append(count)
    active_date.reverse()
    active_count.reverse()

    context={
        'total_count':total_count,
        'mouth_count':mouth_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count,
    }

    return render_template('admin/user_count.html',context=context)






@blue_admin.route('/')
@user_login_data
def admin_index():

    user=g.user
    if not user:
        return redirect(url_for('admin.admin_login'))

    context={
        'user':user.to_dict()
    }

    return render_template('admin/index.html',context=context)

@blue_admin.route('/login',methods=['GET','POST'])
@user_login_data
def admin_login():

    if request.method=='GET':
        user=g.user
        if user and user.is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')


    if request.method == 'POST':
        # 2.1获取参数
        username = request.form.get('username')
        password = request.form.get('password')

        # 2.2校验参数
        if not all([username, password]):
            return render_template('admin/login.html', errmsg='缺少参数')

        # 2.3查询登录用户和校验密码:登录用户必须是管理员的身份
        try:
            user = User.query.filter(User.nick_name == username, User.is_admin == True).first()
        except Exception as e:
            logging.error(e)
            return render_template('admin/login.html', errmsg='查询用户失败')
        if not user:
            return render_template('admin/login.html', errmsg='用户名或密码错误')

        if not user.check_password(password):
            # 密码校验失败才会提示错误
            return render_template('admin/login.html', errmsg='用户名或密码错误')

        # 2.4状态保持
        session['user_id'] = user.id
        # # session['mobile'] = user.mobile
        # # session['nick_name'] = user.nick_name
        session['is_admin'] = user.is_admin # 管理员用户登录时，需要添加身份信息作为状态保持信息，后续会用于检验该用户是否是管理员

        # 2.5响应登录结果
        return redirect(url_for('admin.admin_index'))