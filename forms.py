from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from database import User

# Создаем русские сообщения для валидаторов
class CustomDataRequired(DataRequired):
    def __init__(self, message=None):
        super().__init__(message=message or 'Это поле обязательно для заполнения')

class CustomEmail(Email):
    def __init__(self, message=None):
        super().__init__(message=message or 'Неверный формат электронной почты')

class CustomEqualTo(EqualTo):
    def __init__(self, fieldname, message=None):
        super().__init__(fieldname, message=message or 'Пароли должны совпадать')

class CustomFileAllowed(FileAllowed):
    def __init__(self, upload_set, message=None):
        super().__init__(upload_set, message=message or 'Разрешены только изображения следующих форматов: {}'.format(', '.join(upload_set)))

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[CustomDataRequired()])
    password = PasswordField('Пароль', validators=[CustomDataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[CustomDataRequired()])
    email = StringField('Email', validators=[CustomDataRequired(), CustomEmail()])
    password = PasswordField('Пароль', validators=[CustomDataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[CustomDataRequired(), CustomEqualTo('password')])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другое имя пользователя.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другой email адрес.')

class ProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[CustomDataRequired()])
    email = StringField('Email', validators=[CustomDataRequired(), CustomEmail()])
    current_password = PasswordField('Текущий пароль')
    new_password = PasswordField('Новый пароль')
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[CustomEqualTo('new_password')])
    avatar = FileField('Аватар', validators=[CustomFileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Разрешены только изображения: JPG, PNG, JPEG, GIF')])
    submit = SubmitField('Сохранить изменения')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста, используйте другое имя пользователя.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста, используйте другой email адрес.')