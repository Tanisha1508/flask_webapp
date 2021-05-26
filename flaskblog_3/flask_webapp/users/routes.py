#users blueprint
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_webapp import db, bcrypt
from flask_webapp.db_models import User, Post
from flask_webapp.users.forms import RegisterationForm, LoginForm, UpdateAccountForm,RequestResetForm, ResetPasswordForm
from flask_webapp.users.utils import save_picture, send_reset_email

users=Blueprint('users',__name__) #'users' is the blueprint name

#add routes-->specifically for the users blueprint instead of the global app variable and then register it with our app

@users.route('/register',methods=['GET','POST'])
def register():
    #if user is alread logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    #create instance of our form that we're going to send to our app
    form = RegisterationForm()
    #validate form submit method
    #flash msg-->easy way to send a one time alert 
    if form.validate_on_submit():
        # To hash the pswd entered by the user
        hashed_pswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # now we create a new user
        user = User(username = form.username.data,email=form.email.data,password=hashed_pswd)
        # Now add this user to the changes we want to make in our db
        db.session.add(user)
        db.session.commit()
        #display a msg when we have created a user successfully
        #older way:
        #flash(f"Account created for {form.username.data}!",'success')#categories=success,warning,danger
        #newer way:
        flash("Account created for successfully!",'success')
        return redirect(url_for('users.login'))
    #pass this form to a template
    return render_template('register.html',title='Register',form=form)


@users.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        #older--->
        # if form.email.data=='admin@blog.com' and form.password.data == 'password':
        #     flash("Successfully Logged In!",'success')
        #     return redirect(url_for('main.home'))
        # else:
        #     flash("Login Unsuccessful! Please check username and password.",'danger')
        #     #return redirect(url_for('users.login'))
        #newer--->
        #make sure the user exists:
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            # if there is a next keyword in thje url it redirects to that url
            next_page = request.args.get('next')
            if(next_page):
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful! Please check email and password.",'danger')
    return render_template('login.html',title='Login',form=form)


@users.route("/logout")
def logout():
    logout_user() 
    return redirect(url_for('main.home'))

#how to put certain restrictions on some routes so that you go to them only if you are logged in--->i.e. login before you can view that page
@users.route("/account",methods=['GET','POST'])
@login_required #--you need to login to access this route
def account():
    form = UpdateAccountForm()
    # if our form is valid then we can update our username and email
    if form.validate_on_submit():
        #check if there is any picture data
        if form.picture.data:
            #set the users profile pic
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        #to update:-->when updated the old values will no longer be in the db
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        #flash msg that tells the user that acc has been updtaed
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account'))
    # for the form to display the current username and address when we visit the account
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    #tell where our login route is located?-->init--->login_manager.login_view = 'login'
    #set img file to be passed to the account template
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file,form=form)


#display the posts of inly that user whose username is clicked on
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)#default page no is 1 
    #query for the particular user and then grab their posts
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page = page,per_page=5)
    return render_template('user_posts.html',posts=post,user=user)


@users.route("/reset_password",methods=['GET','POST'])
#user will have to be logged out to access this
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form=RequestResetForm()
    # if form was validated and submitted
    if form.validate_on_submit():
        user =User.query.filter_by(email=form.email.data).first()
        #send email to the user with the token to reset pswd-->send_reset_email fn is used
        send_reset_email(user)
        flash('An email has been sent to reset your password','info')#email is sent using flask_mail in __init__.py
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

#route where user actually resets their pswd:
@users.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    #we have to make sure that its the actual user and the token we gave them in the email is active and we get the token from the url
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    #if invalid token:
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('users.reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_pswd 
        db.session.commit()
        flash("Your password has been updated successfully!",'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html',title='Reset Password',form=form)
    
#add a link to the reset password page to our application
