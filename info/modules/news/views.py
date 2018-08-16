from . import blue_news
from flask import render_template

@blue_news.route('/detail/<int:news_id>')
def news_detail(news_id):
    return render_template('news/detail.html')