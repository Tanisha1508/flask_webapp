#posts blueprint
from flask import render_template, url_for, flash,redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from flask_webapp import db
from flask_webapp.db_models import Post
from flask_webapp.posts.forms import PostForm

posts=Blueprint('posts',__name__) #'users' is the blueprint name

@posts.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm() 
    if form.validate_on_submit():
        # save posts to our db
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html',title='New Post',form=form,legend='New Post')


@posts.route("/post/<int:post_id>")# to add variable in our route-->use angular brackets
def post(post_id):
    #fetch the post if it exists
    # post = Post.query.get(post_id) OR 
    post = Post.query.get_or_404(post_id)#returns a 404 page if the post doesnt exist
    return render_template('post.html',title=post.title,post=post)

@posts.route("/post/<int:post_id>/update",methods=['GET','POST'])
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
        return redirect(url_for('posts.post',post_id=post.id))
    elif request.method=='GET':
        form.title.data=post.title
        form.content.data=post.content
    return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])# only post request when we are going to submit the modal
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))