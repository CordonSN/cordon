from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required
from flask_wtf.file import FileField
from cordon.models import User


class LoginForm(Form):

    nickname = TextField('nickname', validators=[Required()])
    password = TextField('password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(Form):

    nickname = TextField('nickname', validators=[Required()])
    email = TextField('email', validators=[Required()])
    password = TextField('password', validators=[Required()])
    r_password = TextField('r_password', validators=[Required()])


class EditProfileForm(Form):

    name = TextField('name', validators=[Required()])
    bio = TextAreaField('bio')
    sex = TextField('sex')
    slogan = TextField('slogan')
    status = TextField('status')
    location = TextField('location')
    show_email = BooleanField('show_email', default=False)

    '''
    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append(
                'This nickname is already in use. Please choose another one.')
            return False
        return True
    '''


class EditAvatarForm(Form):

    avatar = FileField('avatar')


class EditCoverForm(Form):

    cover = FileField('cover')


class PostForm(Form):

    post = TextAreaField('post', validators = [Required()])
    nsfw = BooleanField('nsfw', default=False)


class CommentForm(Form):

    comment = TextAreaField('comment', validators = [Required()])
