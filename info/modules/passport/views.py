import logging
import random
import re

from flask import abort, jsonify
from flask import make_response
from flask import request
from info import constants
from info import myredis,response_code
from info.libs.yuntongxun.sms import sendTemplateSMS
from info.mytools.captcha.captcha import captcha
from . import blue_passport

@blue_passport.route('/sms_code',methods=['GET','POST'])
def sms_code():
    #1.接受参数 ,手机号,图片验证码,图片uuid
    json_dict=request.json
    mobie=json_dict.get('mobile')
    image_code=json_dict.get('image_code')
    image_code_id=json_dict.get('image_code_id')

    #2.校验参数
    if not all([mobie,image_code,image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少必要参数')

    #3.从redis中取出验证码与用户对比
    if not re.match('^1[345678][0-9]{9}$',mobie):
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
    result=sendTemplateSMS(mobie, [sms_code, 5], 1)
    if result!=0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg='验证码发送失败')


    #6.发送成功,将验证码存到redis,为了下步注册验证用户输入的验证码是否正确

    try:
        myredis.set('sms_code'+mobie,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存验证码失败')
    return jsonify(errno=response_code.RET.OK, errmsg='发送短信验证码成功')


@blue_passport.route('/image_code')
def imageuuid():
    imageuuid=request.args.get('CodeId')

    if not imageuuid:
        print('参数', imageuuid)
        abort(400)
    name, text, image = captcha.generate_captcha()

    # 4.将imageCodeId和图片验证码文字绑定到redis:图片验证码五分钟之后自动的过期
    try:
        myredis.set('ImageCode:'+imageuuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        abort(500)  # 表示服务器错误的

    # 5.响应图片验证码的图片信息给用户
    # 将image作为响应体
    response = make_response(image)
    # 指定响应体数据的类型
    response.headers['Content-Type'] = 'image/jpg'
    return response