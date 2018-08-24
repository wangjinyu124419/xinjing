import logging
import random
import re,datetime
from flask import abort, jsonify
from flask import make_response
from flask import request
from flask import session

from info import constants, db
from info import myredis,response_code
from info.libs.yuntongxun.sms import sendTemplateSMS
from info.models import User
from info.utils.captcha.captcha import captcha
from . import blue_passport
@blue_passport.route('/logout')
#1.清除session保持状态登陆信息
#2.返回退出登陆结果
def logout():
    try:
        session.pop('user_id',None)
        session.pop('is_admin',False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='退出登陆失败')

    return jsonify(errno=response_code.RET.OK, errmsg='退出登陆成 功')


@blue_passport.route('/login',methods=['POST'])
def login():
    #1.接受参数,mobile,password
    json_dict=request.json
    mobile=json_dict.get('mobile')
    password=json_dict.get('password')

    #2.校验参数,参数齐全,手机号格式,

    if not all([mobile,password]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少必要信息')
    if not re.match('^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')
    #3.使用mobile查询user
    try:
        user=User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='手机号或密码错误')
    if not user:
        return jsonify(errno=response_code.RET.DBERR, errmsg='手机号或密码错误')

    # 4.如果user存在,再去校验密码
    if not user.check_password(password):
        return jsonify(errno=response_code.RET.DBERR, errmsg='手机号或密码错误')
    # if not user.check_password(password):
    #     return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')
    #5.如果密码校验通过,记录最后一次登陆时间按,状态保持
    user.last_login=datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存登陆时间失败')

    session['user_id']=user.id
    if user.is_admin:
        session['is_admin'] = True
    #6.响应登陆结果

    return jsonify(errno=response_code.RET.OK, errmsg='登陆成功')


@blue_passport.route('/register',methods=['POST'])
def register():
    #1.接收参数,mobile,password,smscode
    json_dict=request.json
    mobile=json_dict.get('mobile')
    client_smscode=json_dict.get('smscode')
    password=json_dict.get('password')
    #2.校验参数:参数齐全,手机号码格式,
    if not all([mobile,client_smscode,password]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少必要信息')
    if not re.match('^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')
    #3.使用mobile读取服务端短信验证码
    try:
        server_sms_code=myredis.get('sms_code'+mobile)
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='读取数据库短信验证码失败')
    if not server_sms_code:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码过期了')
    #4.服务端验证码与客户端对比
    if server_sms_code!=client_smscode:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='验证码输入错误')

    #5.创建User对象,添加新用户数据
    user=User()

    user.nick_name = mobile
    from werkzeug.security import generate_password_hash, check_password_hash

    user.password=password

    user.mobile = mobile
    # 6.记录最后一次登陆时间
    user.last_login=datetime.datetime.now()

    #7.将用户数据和最后登陆时间保存到mysql
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR,errmsg='保存用户信息失败')
    #8.保持登陆状态保持,写入到session实现注册即登录,只存储一个数据就行?看下session存储到redis数据库的过程

    session['user_id']=user.id

    #9.返回注册结果
    return jsonify(errno=response_code.RET.OK, errmsg='注册成功')


@blue_passport.route('/sms_code',methods=['POST'])
def sms_code():
    #1.接受参数 ,手机号,图片验证码,图片uuid
    json_dict=request.json
    mobile=json_dict.get('mobile')
    image_code=json_dict.get('image_code')
    image_code_id=json_dict.get('image_code_id')

    #2.校验参数
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少必要参数')

    #3.从redis中取出验证码与用户对比
    if not re.match('^1[345678][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    try:
        severimagecode=myredis.get('ImageCode:'+image_code_id)
        print()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='读取验服务器证码失败')
    #判断验证码是否过期
    if not severimagecode:
        return jsonify(errno=response_code.RET.NODATA, errmsg='验证码不存在,过期')

    if image_code.lower()!=severimagecode.lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码错误')



    #4.对比无误生成6位验证码
    sms_code='%06d'%random.randint(0,999999)
    logging.debug(sms_code)
    #5.向用户发送验证码
    result=sendTemplateSMS(mobile, [sms_code, 5], 1)
    if result!=0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='验证码发送失败')


    #6.发送成功,将验证码存到redis,为了下步注册验证用户输入的验证码是否正确

    try:
        myredis.set('sms_code'+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存验证码失败')
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')


@blue_passport.route('/image_code')
def image_code():
    image_code_id=request.args.get('code_id')

    if not image_code_id:
        print('参数', image_code_id)
        abort(400)
    name, text, image = captcha.generate_captcha()

    # 4.将imageCodeId和图片验证码文字绑定到redis:图片验证码五分钟之后自动的过期
    try:
        myredis.set('ImageCode:'+image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        abort(500)  # 表示服务器错误的

    # 5.响应图片验证码的图片信息给用户
    # 将image作为响应体
    response = make_response(image)
    # 指定响应体数据的类型
    response.headers['Content-Type'] = 'image/jpg'
    return response