from qiniu import Auth, put_data


access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'

def upload_file(data):
    """
    上传文件到七牛云
    :param data: 要上传的文件的二进制
    :return: Fg-7WDaDihkttxOclQqZkMC3KUqf
    """

    # 创建Auth对象
    q = Auth(access_key, secret_key)
    # 传入token:token就是bucket_name
    token = q.upload_token(bucket_name)
    # 根据要上传的文件的二进制，上传文件到七牛云
    # 第二个参数写None:目的是为了让七牛云个我们自动的生成图片的唯一标识，而不需要自己去指定文件名字
    ret, info = put_data(token, None, data)
    # 判断上传是否成功
    if info.status_code != 200:
        # 如果上传失败就抛出异常
        raise Exception('七牛上传图片失败')
    # 如果上传成功就返回key
    return ret.get('key')
