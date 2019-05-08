from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password1@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abcdefg'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, owner):
        self.title = title
        self.text = text
        self.owner = owner



@app.route('/', methods=['POST', 'GET'])
def index():
    template = jinja_env.get_template('index.html')
    users = User.query.all()
    return render_template('index.html', title="Users", users=users)


@app.route('/newpost')
def newpost_temp():
    template = jinja_env.get_template('newpost.html')
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST'])
def validate_newpost():
    template = jinja_env.get_template('newpost.html')

    title = request.form['title']
    text = request.form['text']
    owner = User.query.filter_by(username=session['username']).first()

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
           new_blog = Blog(blog_title, blog_text, owner)
           db.session.add(new_blog)
           db.session.commit()
           blog_id = str(new_blog.id)
    
        return redirect('/blog?id='+ blog_id)
    else:
        return template.render(title = title, text = text, title_error = title_error, text_error = text_error)

@app.route('/blog', methods=['GET'])
def blog():
    blog_id=request.args.get('id')
    user_id=request.args.get('user_id')


    if user_id:
        user = User.query.get(user_id)
        template = jinja_env.get_template('user_blogs.html')
        return render_template('user_blogs.html', blogs=user.blogs, owner=user.username)

    if blog_id:
        blog = Blog.query.get(blog_id)
        template = jinja_env.get_template('blog.html')
        return render_template('blog.html', title=blog.title, text=blog.text, owner=blog.owner)

    else:
        blogs = Blog.query.all()
        return render_template('blog_list.html', blogs=blogs)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'main_page', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    template = jinja_env.get_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = ""
        password_error = ""

        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "User does not exist"
        if user and user.password != password:
            password_error = "Password is incorrect"

        if user and user.password == password:
            session['username'] = username
            return redirect('/')
        else:
            return template.render(username_error = username_error, password_error = password_error, username = username)
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/register', methods=['POST', 'GET'])
def register():
    template = jinja_env.get_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ""
        password_error = ""
        verify_error = ""

        if len(username) < 3 or len(username) > 20 or username.count(" ") != 0:
            username_error = "Name must be between 3 and 20 characters in length and cannot contain spaces."
            username = ""

        if len(password) < 3 or len(password) > 20 or password.count(" ") != 0:
            password_error = "Password must be between 3 and 20 characters in length and cannot contain spaces."

        if password != verify:
            verify_error = "Password and confirmation do not match."

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_error = "Username is taken, please choose a different one."
            username = ""

        if not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')

        else:
            return template.render(username_error = username_error, password_error = password_error,
            verify_error = verify_error, username = username,)

    return render_template('signup.html')

if __name__ == '__main__':
    app.run()