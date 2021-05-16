import os
import secrets
from PIL import Image
from flask import render_template,url_for,flash,redirect,request,abort
from flask_webapp import app,db,bcrypt,mail
from flask_webapp.forms import RegisterationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from flask_webapp.db_models import User,Post
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message

# posts = [
#     { 
#         'author': 'Tanisha Garg',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'May 2, 2021'
#     },
#     {
#         'author': 'Jane Austen',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'May 3, 2021'
#     }
# ]


@app.route("/")
@app.route("/home")
def home():
    #grab post from db
    # post = Post.query.all()-->older
    # pagination:
    #to get the requested page number from the url
    page = request.args.get('page',1,type=int)#default page no is 1 
    post = Post.query.order_by(Post.date_posted.desc()).paginate(page = page,per_page=5)
    return render_template('home.html',posts=post)#-->to create static html pages

# to write a code in html template we use code blocks like--> 
# {% for post in posts %}
#     {% endfor %}

@app.route("/about")
def about():
    return render_template('about.html',title='About')


@app.route('/register',methods=['GET','POST'])
def register():
    #if user is alread logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('login'))
    #pass this form to a template
    return render_template('register.html',title='Register',form=form)


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        #older--->
        # if form.email.data=='admin@blog.com' and form.password.data == 'password':
        #     flash("Successfully Logged In!",'success')
        #     return redirect(url_for('home'))
        # else:
        #     flash("Login Unsuccessful! Please check username and password.",'danger')
        #     #return redirect(url_for('login'))
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
                return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful! Please check email and password.",'danger')
    return render_template('login.html',title='Login',form=form)


@app.route("/logout")
def logout():
    logout_user() 
    return redirect(url_for('home'))


#function to save the user profile pic uploaded by the user to our file system
def save_picture(form_picture):
    #we dont wnat to keep the file with the name they uploaded-->randomize the name
    random_hex = secrets.token_hex(8)#8 bytes
    #ensure the file is saved with the same extension it is uploaded
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics', picture_fn)
    #resize the image before saving it to speed up our website---using pillow library
    output_size = (350,500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

#how to put certain restrictions on some routes so that you go to them only if you are logged in--->i.e. login before you can view that page
@app.route("/account",methods=['GET','POST'])
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
        return redirect(url_for('account'))
    # for the form to display the current username and address when we visit the account
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    #tell where our login route is located?-->init--->login_manager.login_view = 'login'
    #set img file to be passed to the account template
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm() 
    if form.validate_on_submit():
        # save posts to our db
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='New Post',form=form,legend='New Post')


@app.route("/post/<int:post_id>")# to add variable in our route-->use angular brackets
def post(post_id):
    #fetch the post if it exists
    # post = Post.query.get(post_id) OR 
    post = Post.query.get_or_404(post_id)#returns a 404 page if the post doesnt exist
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    #ensure that the user who wrote that post can only update the post
    if post.author != current_user:
        abort(403) #403 response is the http response for a forbidden route
    # if the user is the author then we create a form to update post and render template
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        #no need to add as it is already in the db
        db.session.commit()
        flash('Your post has been updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])# only post request when we are going to submit the modal
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


#display the posts of inly that user whose username is clicked on
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)#default page no is 1 
    #query for the particular user and then grab their posts
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page = page,per_page=5)
    return render_template('user_posts.html',posts=post,user=user)


def send_reset_email(user):
    #send user the email with reset token
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])
    msg.body=f'''To reset the password, visit the following link:
{url_for('reset_token',token=token,_external=True)}
 
If you did not make this request then simply ignore this email and no changes will be made.
'''
#_external is used cz we want an absolute url and not a relative url
#for longer/complicated msgs we can use the jinja2 templates
#route to enter the email address to rest the pswd
    mail.send(msg)

@app.route("/reset_password",methods=['GET','POST'])
#user will have to be logged out to access this
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    # if form was validated and submitted
    if form.validate_on_submit():
        user =User.query.filter_by(email=form.email.data).first()
        #send email to the user with the token to reset pswd-->send_reset_email fn is used
        send_reset_email(user)
        flash('An email has been sent to reset your password','info')#email is sent using flask_mail in __init__.py
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

#route where user actually resets their pswd:
@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_token(token):
    #we have to make sure that its the actual user and the token we gave them in the email is active and we get the token from the url
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    #if invalid token:
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_pswd 
        db.session.commit()
        flash("Your password has been updated successfully!",'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)
    
#add a link to the reset password page to our application