from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed #--to upload a profile pic
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField  
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask_webapp.db_models import User

#create forms using classes which then get converted to html templates

#create a registeration form
class RegisterationForm(FlaskForm):
    #different form fields which will be imported classes as well
    #apply checks and validations--use validators--classes imported
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)]) 
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])#can add min len validator also
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    #now we need a submit button that sends the info to us
    submit = SubmitField('Sign Up')

    # create a custom validations by creating a fn here---a template for the validation error
    # def validate_field(self,field):
    #     if True:
    #         raise ValidationError('Validation Message')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose another username!')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose another email address!')


#create a login form
class LoginForm(FlaskForm):
    #username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)]) 
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)]) 
    email = StringField('Email',validators=[DataRequired(),Email()])
    #to upload a pic
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose another username!')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please choose another email address!')


# when we use these forms we need to set a secret key for our app which will protect against modifying cookies 
# and cross-site request forgery attacks etc
# we add a secret key in flask_webapp.py under app


class PostForm(FlaskForm):
    #title of the post:-->every post has to have a title
    title = StringField('Title',validators=[DataRequired()])
    #content of the post-->necessary
    content = TextAreaField('Content',validators=[DataRequired()])
    #submit button to post this to our route
    submit = SubmitField('Post')


#form to reset the pswd by submitting the email:
class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField('Request Password Reset')
    #check/validate if the user has an account or not:
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


#form to pass pswd and conf pswd fields to reset pswd:
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired()])#can add min len validator also
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')
