from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_bootstrap import Bootstrap
from app.models import background_question
from wtforms import Form, TextField, TextAreaField, SubmitField, FieldList, FormField
from wtforms import Form, BooleanField, StringField, PasswordField, validators, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(Form):
    
    questions1 = FieldList(SelectField([validators.InputRequired()]))
    submit = SubmitField("Send")


class TaskForm(Form):
    
    categories1 = FieldList(SelectField([validators.InputRequired()]))
    submit = SubmitField("Send")


class ContinueTaskForm(FlaskForm):
    
    participant_id = StringField('participant_id', validators=[DataRequired()])
    submit = SubmitField('Continue rating')


class StartWithIdForm(FlaskForm):
    
    participant_id = StringField('participant_id', validators=[DataRequired()])
    submit = SubmitField('Start rating')
 

class Questions(FlaskForm):
    
    questions = StringField()


class Answers(FlaskForm):
    
    background_question_idbackground_question = SelectField(coerce=int, validators=[InputRequired])


class BackgroundQuestionForm(Form):
    
    idbackground_question_option = StringField()
    background_question_idbackground_question = StringField()
    option = StringField()
    submit = SubmitField('Register')


class TestForm(Form):
    
    question_name = StringField()
    options1 = SelectField()


class TestForm1(Form):
    
    questions1 = FieldList(SelectField([validators.InputRequired()]))
    submit = SubmitField("Send")


class TestForm2(Form):

    questions1 = SelectField()

#Forms for editing functions
    
    
class CreateExperimentForm(Form):

    name = StringField('Name', [validators.DataRequired()])
    instruction = StringField('Instruction', [validators.DataRequired()])
    language = StringField('Language', [validators.DataRequired()])
    submit = SubmitField('Send')


class EditExperimentForm(Form):

    name = StringField('Name', [validators.DataRequired()])
    instruction = StringField('Instruction', [validators.DataRequired()])
    language = SelectField('Language', choices=[
            ('Afrikanns', 'Afrikanns'), ('Albanian', 'Albanian'), ('Arabic', 'Arabic'), ('Armenian', 'Armenian'), ('Basque', 'Basque'), ('Bengali', 'Bengali'), ('Bulgarian', 'Bulgarian'),
            ('Catalan', 'Catalan'), ('Cambodian', 'Cambodian'), ('Chinese (Mandarin)', 'Chinese (Mandarin)'), ('Croation', 'Croation'), ('Czech', 'Czech'), ('Danish', 'Danish'),
            ('Dutch', 'Dutch'), ('English', 'English'), ('Estonian', 'Estonian'), ('Fiji', 'Fiji'), ('Finnish', 'Finnish'), ('French', 'French'), ('Georgian', 'Georgian'),
            ('German', 'German'), ('Greek', 'Greek'), ('Gujarati', 'Gujarati'), ('Hebrew', 'Hebrew'), ('Hindi', 'Hindi'), ('Hungarian', 'Hungarian'), ('Icelandic', 'Icelandic'),
            ('Indonesian', 'Indonesian'), ('Irish', 'Irish'), ('Italian', 'Italian'), ('Japanese', 'Japanese'), ('Javanese', 'Javanese'), ('Korean', 'Korean'), ('Latin', 'Latin'),
            ('Latvian', 'Latvian'), ('Lithuanian', 'Lithuanian'), ('Macedonian', 'Macedonian'), ('Malay', 'Malay'), ('Malayalam', 'Malayalam'), ('Maltese', 'Maltese'), ('Maori', 'Maori'),
            ('Marathi', 'Marathi'), ('Mongolian', 'Mongolian'), ('Nepali', 'Nepali'), ('Norwegian', 'Norwegian'), ('Persian', 'Persian'), ('Polish', 'Polish'), ('Portuguese', 'Portuguese'),
            ('Punjabi', 'Punjabi'), ('Quechua', 'Quechua'), ('Romanian', 'Romanian'), ('Russian', 'Russian'), ('Samoan', 'Samoan'), ('Serbian', 'Serbian'), ('Slovak', 'Slovak'),
            ('Slovenian', 'Slovenian'), ('Spanish', 'Spanish'), ('Swahili', 'Swahili'), ('Swedish ', 'Swedish '), ('Tamil', 'Tamil'), ('Tatar', 'Tatar'), ('Telugu', 'Telugu'),
            ('Thai', 'Thai'), ('Tibetan', 'Tibetan'), ('Tonga', 'Tonga'), ('Turkish', 'Turkish'), ('Ukranian', 'Ukranian'), ('Urdu', 'Urdu'), ('Uzbek', 'Uzbek'), ('Vietnamese', 'Vietnamese'),
            ('Welsh', 'Welsh'), ('Xhosa', 'Xhosa')])
    submit = SubmitField('Send')


class CreateBackgroundQuestionForm(Form):
    
    bg_questions_and_options = TextAreaField('Background questions and options', [validators.DataRequired()])
    submit = SubmitField('Send')

    
class EditBackgroundQuestionForm(Form):
    
    bg_questions_and_options = TextAreaField('Background questions and options')
    new_values = TextAreaField('New values', [validators.DataRequired()])
    submit = SubmitField('Send')


class CreateQuestionForm(Form):
    
    questions_and_options = TextAreaField('Questions and options', [validators.DataRequired()])
    submit = SubmitField('Send')


class EditQuestionForm(Form): 

    left = StringField('left_scale', [validators.DataRequired()])
    right = StringField('right_scale', [validators.DataRequired()])
    question = StringField('question', [validators.DataRequired()])


class UploadStimuliForm(Form):
    
    type = RadioField('type', choices=[('text', 'text'), ('picture', 'picture'), ('video', 'video'), ('audio', 'audio')])
    text = TextAreaField('Text stimulus')
    media = TextAreaField('Media filename')
    file = FileField('Upload file')
    submit = SubmitField('Send')
    

class EditPageForm(Form):
    
    type = RadioField('type', choices=[('text', 'text'), ('picture', 'picture'), ('video', 'video'), ('audio', 'audio')])
    text = TextAreaField('Text stimulus')
    media = TextAreaField('Media filename')
    file = FileField('Upload file')
    submit = SubmitField('Send')
    
    
class RemoveExperimentForm(Form):
    remove = TextAreaField('Remove')
    submit = SubmitField('Send')

