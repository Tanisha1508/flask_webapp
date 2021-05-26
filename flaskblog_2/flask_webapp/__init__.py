import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app=Flask(__name__)
app.config['SECRET_KEY'] = '50c5219e880d3e37b7627716a4e89a31'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///site.db"
db=SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'#-->fn name of our route
login_manager.login_message_category = 'info' # blue alert
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
#EMAIL_USER and EMAIL_PASS are environ variables in control panel->system security->system->adv settings-->env variables-->user variables
#-->https://www.google.com/settings/security/lesssecureapps
app.config['MAIL_USERNAME']=os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD']=os.environ.get('EMAIL_PASS')
mail = Mail(app)

# to avoid circular imports we add the import here:
from flask_webapp import routes