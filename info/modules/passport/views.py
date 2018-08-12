import logging
from flask import abort
from flask import make_response
from flask import request

from info import constants
from info import myredis
from info.mytools.captcha.captcha import captcha
from . import blue_passport
@blue_passport.route('/image_code')
def imageuuid():
    imageuuid=request.args.get('CodeId')

    if not imageuuid:
        print('参数', imageuuid)
        abort(400)
    name, text, image = captcha.generate_captcha()

    # 4.将imageCodeId和图片验证码文字绑定到redis:图片验证码五分钟之后自动的过期
    try:
        myredis.set('ImageCode:' + imageuuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        abort(500)  # 表示服务器错误的

    # 5.响应图片验证码的图片信息给用户
    # 将image作为响应体
    response = make_response(image)
    # 指定响应体数据的类型
    response.headers['Content-Type'] = 'image/jpg'
    return response