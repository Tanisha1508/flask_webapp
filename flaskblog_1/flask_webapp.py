import datetime
from flask import Flask, render_template,url_for,flash,redirect
# url_for-->function which finds the exact location of the routes for us
from forms import RegisterationForm, LoginForm # import from forms.py both classes and later create its instances
from flask_sqlalchemy import SQLAlchemy
#from db_models import User,Post # this fails because of circular import-->when we import a module that module runs as a whole and not only the part being imported
# we create a package of the application so we create a folder flask_webapp and create __init__.py in that folder
app=Flask(__name__)

#set a secret key---set config values on our app
#it can be some random characters
# in cmd we write the following commands:
# python
# import secrets
# secrets.token_hex(16)-->16 bytes
# '50c5219e880d3e37b7627716a4e89a31'-->this what we get as random chars
app.config['SECRET_KEY'] = '50c5219e880d3e37b7627716a4e89a31'

'''Add databases:create a database using Flask-SQLAlchemy. 
URI for databse which is where the database is located 
Use SQLite database as it is the easiest to get upand running with and this db will simply be a 
file on our file system so to set the location of the db we need to set it as configuration.'''
# 3 frwd slashes to specify a relative path from the current file so asite .db file is created in this directory
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///site.db"

# create a db instance
db=SQLAlchemy(app)
# with SQLAlchemy we can represent our db structure as classes called models--put in a diff folder 
# each class is going to be its own table in the db

class User(db.Model):
    # add columns for this table
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    # for user's profile pic
    image_file = db.Column(db.String(120),nullable=False,default='default.jpg')# hash the img files that are 20 characters long so that they are all unique
    #there will be a default prfile pic always 
    # passwords have to be hashed using hashing algos so they will be 60 chars long after being hashed
    password = db.Column(db.String(60),nullable=False)
    # posts attribute has a relationship to the Post model to get all the posts created by a user, 
    # backref is similar to adding another column to post model so it gets the user who created the post,
    # lazy arg defines when sqlalchemy loads the data frm the db,lazy=True means that sqlalchemy will load the data as necessary in one go
    # posts is just a relationship not a column--just sort of query in the bg
    posts = db.relationship('Post',backref='author',lazy=True)

    # double underscore methods OR dunder methods OR magic methods
    def __repr__(self): # how our object is printed
        return f"User('{self.username}','{self.email}',{self.image_file}')"

# post class to hold our posts
class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)# Coordinated Universal Time (UTC)
                                                                          #try datetime.now
    content = db.Column(db.Text,nullable=False)
    # to specify the user in the post model we can add the id for the author
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)# id of user wh authored the post
    # above the ForeignKey is referencing to table name and column name
    def __repr__(self): # how our object is printed
        return f"User('{self.title}','{self.date_posted}')"

# post model and user model will have a relationship since users will author posts--one-to-many relationship
# To create the db through cmd--->steps in documentation.txt




posts = [
    {
        'author': 'Tanisha Garg',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'May 2, 2021'
    },
    {
        'author': 'Jane Austen',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'May 3, 2021'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',posts=posts)#-->to create static html pages

# to write a code in html template we use code blocks like--> 
# {% for post in posts %}
#     {% endfor %}

@app.route("/about")
def about():
    return render_template('about.html',title='About')


@app.route('/register',methods=['GET','POST'])
def register():
    #create instance of our form that we're going to send to our app
    form = RegisterationForm()
    #validate form submit method
    #flash msg-->easy way to send a one time alert 
    if form.validate_on_submit():
        #display a msg when we have created a user successfully
        flash(f"Account created for {form.username.data}!",'success')#categories=success,warning,danger
        return redirect(url_for('home'))
    #pass this form to a template
    return render_template('register.html',title='Register',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data=='admin@blog.com' and form.password.data == 'password':
            flash("Successfully Logged In!",'success')
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful! Please check username and password.",'danger')
            #return redirect(url_for('login'))
    return render_template('login.html',title='Login',form=form)

if __name__=="__main__":
    app.run(debug=True)


#ctrl shift R for hard refresh--clear cache
# template inheritence so that we don't have to reapeat the code and just write the unique code
# a block is the part in template which the children templates can override
# so we create a block in layout.html
