import logging
from redis import StrictRedis


class Config(object):
    DEBUG=True
    # SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/flaskdb_1"
    # SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:124419@127.0.0.1:3306/information'
    # 禁用追踪mysql:因为mysql的性能差，如果再去追踪mysql的所有的修改，会再次浪费性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    redisip='127.0.0.1'
    redisport=6379
    SECRET_KEY  = '0'
    #配置大写Session
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host=redisip,port=redisport)
    # SESSION_USE_SIGNER=True
    PERMANENT_SESSION_LIFETIME=24*60*60

class Devconfig(Config):
    DEBUG=True
    loglevel=logging.DEBUG


class Proconfig(Config):
    DEBUG = False
    loglevel=logging.ERROR


dictconfig={
    'dev':Devconfig,
    'pro':Proconfig
}
