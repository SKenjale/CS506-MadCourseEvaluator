from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField, SearchField,EmailField,TextAreaField
from wtforms.validators import DataRequired, EqualTo, AnyOf,InputRequired,NoneOf

"""CR: The name of the class corresponds to the form that it calls"""
class LoginForm(FlaskForm):
    """
    Input Fields for user to input login information
    A form is considered submitted when:
        username field and password field have text
    """
    username = StringField("Username:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")


class SignupForm(FlaskForm):
    """
    Input Fields for user to input signup information
    A form is considered submitted when:
        username field has text
        password1 field has text and matches password 2
        password 2 has text
    """

    #CR: Add validator to ensure password lengths
    #CR: Ensure that the message is displayed
    username = StringField("Username:", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired()])
    password1 = PasswordField("Password:", validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField("Retype Password:", validators=[DataRequired()])
    submit = SubmitField("Sign Up")
    

class SearchForm(FlaskForm):

    def values_formatter(v:list):
        return ", ".join(str(x).lower() for x in v)
    #CR: Mention where it is used
    #CR: Mention what it is used for
    injection_list = ['sql','drop', ';',"insert","select"] 
    injection_message = "Dont try a sql injection"
    NoneValidator = NoneOf(values= injection_list,message=injection_message, values_formatter=values_formatter)
    
    searchInput = SearchField("Search Classes...", validators=[InputRequired(),NoneValidator])
    submit = SubmitField("Submit")



    



class UserDataForm(FlaskForm):
    """A generic form to collect data from the user. Used by view functions
    professorsInfo and classesinfo. The form has 3 elements: text for the user
    to type the text, rating to collect the rating of the professor or the class,
    ans=d a submit button.
    """

    text = TextAreaField("Leave a comment", validators=[InputRequired()])
    _values = ["1","2","3","4","5"]
    _message = "Integer between 1 and 5 inclusive"
    rating = StringField(_message, validators=[AnyOf(_values, message=_message)])
    submit = SubmitField("submit");
