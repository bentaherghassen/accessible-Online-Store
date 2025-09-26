from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user, logout_user
from app.models import Product, Newsletter, User, Review, Order
from app.forms import NewsletterForm, UpdateProfileForm, UpdatePasswordForm, DeleteAccountForm
from app import db, bcrypt
from app.utils import save_picture
from sqlalchemy import func
from datetime import datetime, timedelta
from app.utils import get_client_of_the_week


main_bp = Blueprint('main', __name__)


@main_bp.route("/")
@main_bp.route("/home")
def home():
    featureds_products = Product.query.order_by(Product.price.desc()).limit(4).all()
    random_reviews = Review.query.order_by(func.random()).limit(5).all()
    client_of_the_week = get_client_of_the_week()
    return render_template("home.html", featureds=featureds_products, reviews=random_reviews, client_of_the_week=client_of_the_week)

@main_bp.route("/about")
def about():
    return render_template("about.html", title="About")

@main_bp.route("/profile/<string:username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    products = Product.query.filter_by(uploader=user).order_by(Product.id.desc()).all()
    return render_template("profile.html", title=f"{user.username}'s Profile", user=user, products=products)

@main_bp.route("/account", methods=["GET", "POST"])
@login_required
def account_settings():
    update_profile_form = UpdateProfileForm()
    update_password_form = UpdatePasswordForm()
    delete_account_form = DeleteAccountForm()

    if request.method == "POST":
        if update_profile_form.submit_profile.data and update_profile_form.validate_on_submit():
            if update_profile_form.picture.data:
                picture_file = save_picture(update_profile_form.picture.data, "static/media/user_pics", output_size=(150, 150))
                current_user.image_file = picture_file
            current_user.fname = update_profile_form.fname.data
            current_user.lname = update_profile_form.lname.data
            current_user.username = update_profile_form.username.data
            current_user.email = update_profile_form.email.data
            current_user.bio = update_profile_form.bio.data
            current_user.phone_number = update_profile_form.phone_number.data
            current_user.gender = update_profile_form.gender.data
            current_user.home_address = update_profile_form.home_address.data
            db.session.commit()
            flash("Your profile has been updated!", "success")
            return redirect(url_for('main.account_settings'))

        elif update_password_form.submit_password.data and update_password_form.validate_on_submit():
            if not bcrypt.check_password_hash(current_user.password, update_password_form.current_password.data):
                flash("Incorrect current password.", "danger")
            else:
                hashed_password = bcrypt.generate_password_hash(update_password_form.new_password.data).decode("utf-8")
                current_user.password = hashed_password
                db.session.commit()
                flash("Your password has been updated!", "success")
            return redirect(url_for('main.account_settings'))

        elif delete_account_form.submit_delete.data and delete_account_form.validate_on_submit():
            if not bcrypt.check_password_hash(current_user.password, delete_account_form.password.data):
                flash("Incorrect password. Account not deleted.", "danger")
            else:
                user_to_delete = User.query.get(current_user.id)
                logout_user()
                if user_to_delete:
                    db.session.delete(user_to_delete)
                    db.session.commit()
                    flash("Your account has been permanently deleted.", "success")
                    return redirect(url_for('main.home'))
                else:
                    flash("An error occurred. User not found.", "danger")

    elif request.method == "GET":
        update_profile_form.fname.data = current_user.fname
        update_profile_form.lname.data = current_user.lname
        update_profile_form.username.data = current_user.username
        update_profile_form.email.data = current_user.email
        update_profile_form.gender.data = current_user.gender
        update_profile_form.home_address.data = current_user.home_address
        update_profile_form.phone_number.data = current_user.phone_number
        update_profile_form.bio.data = current_user.bio

    image_file = url_for("static", filename=f"media/{current_user.image_file}") if current_user.image_file else url_for('static', filename='default.png')

    return render_template("account.html",
                           title="Account Settings",
                           update_profile_form=update_profile_form,
                           update_password_form=update_password_form,
                           delete_account_form=delete_account_form,
                           image_file=image_file)

@main_bp.route("/newsletter_subscribe", methods=["POST"])
def newsletter_subscribe():
    form = NewsletterForm()
    if form.validate_on_submit():
        email = form.email.data
        existing_subscriber = Newsletter.query.filter_by(email=email).first()
        if existing_subscriber:
            flash("You are already subscribed to our newsletter!", "info")
        else:
            subscriber = Newsletter(email=email)
            db.session.add(subscriber)
            db.session.commit()
            flash("Thank you for subscribing to our newsletter!", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")

    return redirect(request.referrer or url_for('main.home'))
