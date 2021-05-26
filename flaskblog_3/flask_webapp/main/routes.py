#home and about blueprint
from flask import render_template, request, Blueprint
from flask_webapp.db_models import Post

main=Blueprint('main',__name__) #'users' is the blueprint name

@main.route("/")
@main.route("/home")
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

@main.route("/about")
def about():
    return render_template('about.html',title='About')

