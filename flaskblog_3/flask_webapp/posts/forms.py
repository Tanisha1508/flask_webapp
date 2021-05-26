from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    #title of the post:-->every post has to have a title
    title = StringField('Title',validators=[DataRequired()])
    #content of the post-->necessary
    content = TextAreaField('Content',validators=[DataRequired()])
    #submit button to post this to our route
    submit = SubmitField('Post')

