# older-->from flask_webapp import db # from __main__ import db--->create db instance before importing db_models in flask_webapp.py-->ugly solution
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #for a time based token to reset pswd
from flask_webapp import db,login_manager,app # from __init__.py
from flask_login import UserMixin # for some extra attributes in our user class or model like isAuthenticated, isActive etc

#create fn with a decorator called user loader for reloading the user from userid stored in the session     
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
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

    #method to create time based tokens:
    def get_reset_token(self,expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        #now we create & return a token:
        return s.dumps({'user_id':self.id}).decode('utf-8')#we have to pass a user id for this payload in dumps.decode

    #method that verifies he token:
    @staticmethod #method w/o self-->not to expect self as an argument
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        #the token maybe invalid or expired so we use a try and except block:
        try:
            user_id = s.loads(token)['user_id']
        except: 
            return None
        #if no exception then return the user with that id:
        return User.query.get(user_id)


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