
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired

class BaseForm(FlaskForm):
    submit = SubmitField('Submit')

    def __init__(self, submit_button_text, *args, **kwargs):
        setattr(self, 'submit', SubmitField(submit_button_text))
        super(BaseForm, self).__init__(*args, **kwargs)

class AuthenticationForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, submit_button_text, *args, **kwargs):
        super().__init__(submit_button_text, *args, **kwargs)

class LoginForm(AuthenticationForm):
    remember_me = BooleanField('Remember Me')

    def __init__(self, *args, **kwargs):
        super().__init__('Sign In', *args, **kwargs)

class PostForm(BaseForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('SubTitle', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    image_path = FileField('Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    should_delete_blob = HiddenField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__('Save', *args, **kwargs)

class RegisterForm(AuthenticationForm):
    re_password = PasswordField('Re-Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__('Register', *args, **kwargs)