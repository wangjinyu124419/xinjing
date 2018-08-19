import logging
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from info import constants
from info import response_code, db
from info.models import User
from info.utils.file_storage import upload_file
from . import blue_user
from  info.utils.comment import user_login_data

@blue_user.route('/collection',methods=['GET','POST'])
@user_login_data
def user_collection():
    # 1.查询登录用户基本信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    #2.收藏界面
    if request.method=='GET':
        # 2.1接受参数
        page=request.args.get('p',1)
        try:
            page=int(page)
        except Exception as e:
            logging.error(e)
            page=1
        news_list=[]
        currentPage=1
        totalPage=1
        try:
            paginate=user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg='分页查询失败')
        currentPage=paginate.page
        totalPage=paginate.pages
        news_list=paginate.items
        news_dict_list=[]
        print(news_list)
        for news  in news_list:
            news_dict_list.append(news.to_dict())

        context = {
            'user': user.to_dict(),
            'news_dict_list':news_dict_list,
            'current_page':currentPage,
            'total_page':totalPage

        }
        return render_template('news/user_collection.html',context=context )



@blue_user.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    # 1.查询登录用户基本信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    #2.展示密码界面
    if request.method=='GET':
        # context = {
        #     'user': user.to_dict()
        # }
        return render_template('news/user_pass_info.html', )
    #3.修改密码
    #3.1接受参数

    if request.method == 'POST':
            # 3.1 接受参数：old_password,new_password
            old_password = request.json.get('old_password')
            new_password = request.json.get('new_password')

            # 3.2 校验参数：判断参数是否齐全，判断old_password是否是当前登录用户的原始密码
            if not all([old_password, new_password]):
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

            if not user.check_password(old_password):
                print(user.check_password(old_password))
                return jsonify(errno=response_code.RET.PARAMERR, errmsg='旧密码参数')

            # 3.3 将新的密码同步到数据库(核心代码)
            user.password = new_password
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.error(e)
                return jsonify(errno=response_code.RET.DATAERR, errmsg='保存新密码失败')

            # 3.5.响应修改结果
            return jsonify(errno=response_code.RET.OK, errmsg='密码修改成功')

@blue_user.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    # 1.查询登录用户基本信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    #2.展示用户头像
    if request.method=='GET':
        context = {
            'user': user.to_dict()
        }
        return render_template('news/user_pic_info.html', context=context)

    #3.修改用户头像
    if request.method == 'POST':
        #3.1接受图片二进制信息
        image_data=request.files.get('avatar')
        print(type(image_data))
        #3.2判断二进制文件传送成功
        try:
            avatar_data=image_data.read()
            print(type(avatar_data))

        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.PARAMERR,errmsg='读取图片失败')


        #3.3.调用qiniu函数上传
        try:
            key=upload_file(avatar_data)
        except Exception as e:
            logging.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传七牛云失败')

        # user.avatar_url=constants.QINIU_DOMIN_PREFIX+key
        user.avatar_url=key
        #3.3 同步到数据库
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DATAERR, errmsg='保存用户头像失败')
        data={
            'avatar_url':constants.QINIU_DOMIN_PREFIX+key

        }
        #3.4返回上传结果
        return jsonify(errno=response_code.RET.OK, errmsg='Ok',data=data)


@blue_user.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    # 1.查询登录用户基本信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    #2展示用户资料GET
    if request.method=='GET':

        pass
        # 2.构造渲染用户界面的数据

        context = {
            'user': user.to_dict()
        }
        # 3.渲染用户界面
        return render_template('news/user_base_info.html', context=context)
    #3修改用户资料POST
    if request.method == 'POST':
        pass
        # 3.1接受参数,
        json_dict=request.json
        nick_name=json_dict.get('nick_name')
        signature=json_dict.get('signature')
        gender=json_dict.get('gender')
        # 3.2校验参数
        if not all(['json_dict','nick_name','gender']):
            return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR,errmsg='性别错误')

        # 3.3修改用户数据
        user.nick_name=nick_name
        user.signature=signature
        user.gender=gender
    #   修改昵称后同步到状态保持
#       session['nick_name']=nick_name

        # 3.4同步到数据库

        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR,errmsg='保存到数据库失败')

        # 3.5返回修改结果
        return jsonify(errno=response_code.RET.OK, errmsg='Ok')


@blue_user.route('/user_info')
@user_login_data
def user_info():
# 1.查询登录用户基本信息
    user=g.user
    if not user:
        return redirect(url_for('index.index'))
# 2.构造渲染用户界面的数据
    #2.1接受参数,
    #2.2校验参数
    context={
        'user':user.to_dict()
    }
# 3.渲染用户界面


    return render_template('news/user.html',context=context)