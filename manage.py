from flask import Flask
#创建app实例
app=Flask(__name__)

#配置app
class Config(object):
    DEBUG=True

app.config.from_object(Config)


@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    pass
    app.run()

