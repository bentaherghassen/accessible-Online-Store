from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import bcrypt, db
from flask_login import login_user, current_user, logout_user
from app.models import User
from app.forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm
from app.hundlers import send_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    # Check if there are any users in the database
    first_user = User.query.first()
    # Set is_admin to True if this is the first user, otherwise False
    is_admin_status = True if first_user is None else False
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            fname=form.fname.data,
            lname=form.lname.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            gender = form.gender.data,
            home_address = form.home_address.data,
            phone_number = form.phone_number.data,
            is_admin=is_admin_status
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully for {form.username.data}", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", title="Register", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # If the user is banned, prevent login and flash a message.
            if user.is_banned:
                flash("Your account has been banned. Please contact support for more information.", "danger")
                return redirect(url_for("auth.login"))
            # Successful login: reset failed attempts
            user.failed_login_attempts = 0
            db.session.commit()
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            # Failed login attempt
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 3:
                    user.is_banned = True
                    flash("Too many failed login attempts. Your account has been banned.", "danger")
                else:
                    flash("Login Unsuccessful. Please check credentials", "danger")
                db.session.commit()
            else:
                flash("Login Unsuccessful. Please check credentials", "danger")
    return render_template("login.html", title="Login", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@auth_bp.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash(
            "If this account exists, you will receive an email with instructions","info")
        return redirect(url_for("auth.login"))
    return render_template("reset_request.html", title="Reset Password", form = form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("The token is invalid or expired", "warning")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        db.session.commit()
        flash(f"Your password has been updated. You can now log in", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", title="Reset Password", form=form)
