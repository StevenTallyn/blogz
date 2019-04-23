from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Password1@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(256))

    def __init__(self, title, text):
        self.title = title
        self.text = text


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    template = jinja_env.get_template('todos.html')
    blogs = Blog.query.all()
    return render_template('todos.html',title="Blogs", 
        blogs=blogs)

@app.route('/newpost')
def newpost_temp():
    template = jinja_env.get_template('newpost.html')
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST'])
def validate_newpost():
    template = jinja_env.get_template('newpost.html')

    title = request.form['title']
    text = request.form['text']

    title_error = ""
    text_error = ""

    if not title:
        title_error = "This blog needs a title!"

    if not text:
        text_error = "This blog needs some text!"

    if not title_error and not text_error:
        if request.method == 'POST':
           blog_title = request.form['title']
           blog_text = request.form['text']
           new_blog = Blog(blog_title, blog_text)
           db.session.add(new_blog)
           db.session.commit()
        return redirect('/blog')
    else:
        return template.render(title = title, text = text, title_error = title_error, text_error = text_error)

if __name__ == '__main__':
    app.run()