from flask import Flask

app=Flask(__name__)

@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    pass
    app.run(debug=True)

