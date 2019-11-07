from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class Title_Year(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit')