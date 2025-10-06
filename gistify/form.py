from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from gistify.model import User
from flask_login import current_user 
from wtforms import ValidationError
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    preference = SelectField('Preference',
                         choices=[
                             ('summary', 'Summary Notes'),          # short + concise
                             ('detailed', 'Detailed Notes'),        # more in-depth
                             ('bullet', 'Bullet Points'),           # quick bullets
                             ('keywords', 'Key Terms & Concepts'),  # only key terms
                             ('action', 'Action Items / Steps'),    # if it's tutorial
                             ('quiz', 'Quiz Questions')             # AI generates Q&A
                         ],
                         validators=[DataRequired()])
    tone = SelectField('Tone / Style',
                   choices=[
                       ('simple', 'Simple & Easy to Understand'),
                       ('academic', 'Academic / Formal'),
                       ('professional', 'Professional / Business'),
                       ('creative', 'Creative & Engaging'),
                       ('child', 'Child-Friendly'),
                       ('technical', 'Technical / Detailed')
                   ],
                   validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(Self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username Already exists, try something else")
    def validate_email(Self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email Already exists, sign-in instead")

class loginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    preference = SelectField('Preference',
                         choices=[
                             ('summary', 'Summary Notes'),          # short + concise
                             ('detailed', 'Detailed Notes'),        # more in-depth
                             ('bullet', 'Bullet Points'),           # quick bullets
                             ('keywords', 'Key Terms & Concepts'),  # only key terms
                             ('action', 'Action Items / Steps'),    # if it's tutorial
                             ('quiz', 'Quiz Questions')             # AI generates Q&A
                         ],
                         validators=[DataRequired()])
    tone = SelectField('Tone / Style',
                   choices=[
                       ('simple', 'Simple & Easy to Understand'),
                       ('academic', 'Academic / Formal'),
                       ('professional', 'Professional / Business'),
                       ('creative', 'Creative & Engaging'),
                       ('child', 'Child-Friendly'),
                       ('technical', 'Technical / Detailed')
                   ],
                   validators=[DataRequired()])
    picture = FileField('Update Profile Picture', 
                        validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(Self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username Already exists, try something else")
    def validate_email(Self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email Already exists, try something else")
    def validate_preference(Self, preference):
        if current_user.preference != preference.data:
            user = User.query.filter_by(preference=preference.data).first()
            if user:
                raise ValidationError("The provided preference is already being used.")
    def validate_tone(Self, tone):
        if current_user.tone != tone.data:
            user = User.query.filter_by(tone=tone.data).first()
            if user:
                raise ValidationError("The provided tone is already being used.")
    
# class LinkForm(FlaskForm):
#     link = StringField('Paste Link Here', validators=[DataRequired()],
#                        render_kw={"placeholder": "Paste YouTube link"})
#     submit = SubmitField('Generate Notes')

#     def validate_link(self, link):
#         url = link.data.strip()
#         if 'list' in url:
#             raise ValidationError("Playlist links are not allowed. Please provide a single video link.")
#         # 2️⃣ Check if the link looks like a valid URL
#         url_pattern = re.compile(
#             r'^(https?://)?'            # http:// or https://
#             r'([a-zA-Z0-9_-]+\.)+'      # domain...
#             r'([a-zA-Z]{2,})'           # top-level domain
#             r'(/[a-zA-Z0-9&%_\./-~-]*)?$' # path (optional)
#         )
#         if not url_pattern.match(url):
#             raise ValidationError("Please enter a valid URL.")

class LinkForm(FlaskForm):
    link = StringField(
        'Paste Link Here',
        validators=[DataRequired()],
        render_kw={"placeholder": "Paste YouTube link"}
    )

    cookies_file = FileField(
        'Upload cookies.txt (optional)',
        validators=[FileAllowed(['txt'], 'Only .txt files are allowed')]
    )

    submit = SubmitField('Generate Notes')

    def validate_link(self, link):
        url = link.data.strip()
        if 'list' in url:
            raise ValidationError("Playlist links are not allowed. Please provide a single video link.")

        # Check if URL looks valid
        url_pattern = re.compile(
            r'^(https?://)?'                # http:// or https://
            r'([a-zA-Z0-9_-]+\.)+'          # domain...
            r'([a-zA-Z]{2,})'               # top-level domain
            r'(/[a-zA-Z0-9&%_\./-~-]*)?$'   # path (optional)
        )
        if not url_pattern.match(url):
            raise ValidationError("Please enter a valid URL.")
        
class GenerateNotesForm(FlaskForm):
    submit = SubmitField("Generate Detailed Notes")