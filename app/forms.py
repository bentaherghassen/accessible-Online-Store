from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField,IntegerField,DecimalField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Regexp,
    EqualTo,
    ValidationError,
)
from app.models import User, Newsletter,Category
from wtforms_sqlalchemy.fields import QuerySelectField


class RegistrationForm(FlaskForm):
    fname = StringField(
        "First Name :", validators=[DataRequired(), Length(min=2, max=25)]
    )
    lname = StringField("Last Name :", validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField(
        "Username :", validators=[DataRequired(), Length(min=2, max=25)]
    )
    email = StringField("Address E-mail :", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password :",
        validators=[
            DataRequired(),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,32}$"
            ),
        ],
    )
    confirm_password = PasswordField(
        "Password :", validators=[DataRequired(), EqualTo("password")]
    )
    gender = RadioField('Gender :',
                        choices=[('Male', 'Male'), ('Female', 'Female')],
                        validators=[DataRequired()])

    phone_number = StringField('Phone Number :',
                               validators=[DataRequired(),
                                           Length(min=10, max=15),
                                           Regexp(r'^\+?\d{10,15}$',
                                                  message="Invalid phone number format.")])

    home_address = TextAreaField('Home Address :',
                                 validators=[DataRequired(), Length(min=10, max=200)])

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists! Please choose a different one"
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists! Please choose a different one")


class LoginForm(FlaskForm):
    email = StringField("Address E-mail :", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password :",
        validators=[
            DataRequired(),
        ],
    )
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Request ')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,32}$"
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Reset Password")


class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password", validators=[DataRequired()]
    )
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&_])[A-Za-z\\d@$!%*?&_]{8,32}$"
            ),
        ],
    )
    confirm_new_password = PasswordField(
        "Confirm New Password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit_password = SubmitField("Update Password")


class UpdateProfileForm(FlaskForm):
    fname = StringField(
        "First Name:", validators=[DataRequired(), Length(min=2, max=25)]
    )
    lname = StringField("Last Name:", validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField(
        "Username:", validators=[DataRequired(), Length(min=2, max=25)]
    )
    email = StringField("Address E-mail :", validators=[DataRequired(), Email()])
    bio = TextAreaField("Bio :")
    gender = RadioField('Gender :',
                        choices=[('Male', 'Male'), ('Female', 'Female')],
                        validators=[DataRequired()])

    phone_number = StringField('Phone Number :',
                               validators=[DataRequired(),
                                           Length(min=10, max=15),
                                           Regexp(r'^\+?\d{10,15}$',
                                                  message="Invalid phone number format.")])

    home_address = TextAreaField('Home Address :',
                                 validators=[DataRequired(), Length(min=10, max=200)])
    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit_profile = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "Username already exists! Please choose a different one"
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "Email already exists! Please choose a different one"
                )


class DeleteAccountForm(FlaskForm):
    password = PasswordField('Current Password', validators=[DataRequired()])
    submit_delete = SubmitField('Delete Account')

# New form for newsletter
class NewsletterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField("Description")
    price = DecimalField("Price", validators=[DataRequired()], places=2)
    stock = IntegerField("Stock", validators=[DataRequired()])
    category = QuerySelectField(
    'Category',
    query_factory=lambda: Category.query.all(),
    get_pk=lambda a: a.id,
    get_label=lambda a: a.name,
    allow_blank=True,  # This allows the field to be optional
    blank_text="-- Select a Category --",  # Optional: Adds a blank option
    )
    new_category_name = StringField("Or Add New Category")
    image = FileField("Product Image", validators=[FileAllowed(["jpg", "png", "jpeg"])])
    submit = SubmitField("Submit")

class AdminEditUserForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=25)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin')
    submit = SubmitField('Update User')

    def __init__(self, user, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, username):
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
