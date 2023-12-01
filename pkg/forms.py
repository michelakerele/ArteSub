from flask_wtf import FlaskForm,RecaptchaWidget
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,SubmitField,SelectMultipleField,widgets,validators,SelectField
from wtforms.validators import Email,DataRequired,EqualTo,Length
from flask_wtf.file import FileField, FileRequired,FileAllowed


class RegForm(FlaskForm):
    FirstName= StringField('Fullname',validators=[DataRequired()])
    Username= StringField('Username',validators=[DataRequired()])
    Email= StringField('Email',validators=[Email(),DataRequired()])
    Password= PasswordField('Password',validators=[DataRequired()])
    ConfirmPassword= PasswordField('Confirm Password',validators=[EqualTo('Password')])
    btn=SubmitField('Register',validators=[DataRequired()])


class LogForm(FlaskForm):
    Username= StringField(validators=[DataRequired(),Length(min=2)])
    Password= PasswordField('Password',validators=[DataRequired()])
    btn=SubmitField('Register',validators=[DataRequired()]) 


class DpForm(FlaskForm):
    dp = FileField("Upload a Profile Piture",validators=[FileRequired(),FileAllowed(["jpg","png","jpeg"])])
    btnupload = SubmitField("Upload Picture")

class AlbumForm(FlaskForm):
    album_title = StringField('Album Title', validators=[validators.InputRequired()])
    album_tracks = SelectMultipleField('Select Tracks', coerce=int)
    cover_art = FileField('Cover Art', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPEG or PNG images are allowed.')
    ])
    submit = SubmitField('Create Album')


class PlaylistForm(FlaskForm):
    playlist_title = StringField('Playlist Title', validators=[DataRequired()])
    selected_tracks = SelectField('Selected Tracks', coerce=int)  # This field will display the available tracks for selection