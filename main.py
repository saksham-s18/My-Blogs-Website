from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm,LoginForm,CommentForm
from flask_gravatar import Gravatar
import os
from dotenv import load_dotenv
import smtplib

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] =os.environ.get('FLASK_KEY')
ckeditor = CKEditor(app)
Bootstrap5(app)
login_manager=LoginManager()
login_manager.init_app(app)

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))

class User(UserMixin,db.Model):
    __tablename__="users"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    email:Mapped[str]=mapped_column(String,unique=True)
    password:Mapped[str]=mapped_column(String,nullable=False)
    name:Mapped[str]=mapped_column(String,nullable=False)
    posts=relationship("BlogPost",back_populates="author")
    comments=relationship("Comment",back_populates="comment_author")
# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id:Mapped[int]=mapped_column(Integer,db.ForeignKey("users.id"))
    author=relationship("User",back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments=relationship("Comment",back_populates="parent_post")

class Comment(db.Model):
    __tablename__="comments"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    text:Mapped[str]=mapped_column(Text,nullable=False)
    author_id:Mapped[int]=mapped_column(Integer,db.ForeignKey("users.id"))
    comment_author=relationship("User",back_populates="comments")
    post_id:Mapped[int]=mapped_column(Integer,db.ForeignKey("blog_posts.id"))
    parent_post=relationship("BlogPost",back_populates="comments")

with app.app_context():
    db.create_all()

gravatar=Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not current_user.is_authenticated or current_user.id!=1:
            return abort(code=403)
        return f(*args,**kwargs)
    return decorated_function

@app.route('/register',methods=["GET","POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=db.session.execute(db.select(User).where(User.email==form.email.data)).scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        hashed_pass=generate_password_hash(form.password.data,method='pbkdf2:sha256',salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hashed_pass,
            name=form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html",form=form,current_user=current_user)


@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=db.session.execute(db.select(User).where(User.email==form.email.data)).scalar()
        password=form.password.data
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html",form=form,current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts,current_user=current_user)


@app.route("/post/<int:post_id>",methods=['GET','POST'])
def show_post(post_id):
    comment_form=CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in to comment.")
            return redirect(url_for("login"))
        new_comment=Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post",post_id=post_id))
    return render_template("post.html", post=requested_post,current_user=current_user,form=comment_form)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True,current_user=current_user)

@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html",current_user=current_user)


MAIL_ADDRESS = os.environ.get("EMAIL_KEY")
MAIL_APP_PW = os.environ.get("PASSWORD_KEY")
print("MAIL:", MAIL_ADDRESS)
print("PASS:", MAIL_APP_PW)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"""\
From: {MAIL_ADDRESS}
To: sakshamsingh1876@gmail.com
Subject: New Contact Form Message

Name: {name}
Email: {email}
Phone: {phone}
Message: {message}
"""
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MAIL_ADDRESS, MAIL_APP_PW)  # must be valid Gmail + app password
        connection.sendmail(
            from_addr=MAIL_ADDRESS,
            to_addrs="sakshamsingh1876@gmail.com",
            msg=email_message
        )


if __name__ == "__main__":
    app.run(debug=False, port=5002)
