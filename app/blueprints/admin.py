import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from app import app, db
from flask_login import login_required, current_user
from app.utils import save_picture,delete_picture
from app.decorators import admin_required
from app.models import User, Product, Order, Newsletter,Cart,Category
from app.forms import AdminEditUserForm, ProductForm



admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.context_processor
def inject_pending_orders_count():
    pending_orders_count = Order.query.filter_by(status='Pending').count()
    return dict(pending_orders_count=pending_orders_count)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Logic condition 1: Prevent an admin from deleting themselves
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('admin.users'))
    # Logic condition 2: Prevent deleting the last admin account
    admin_count = User.query.filter_by(is_admin=True).count()
    if user.is_admin and admin_count == 1:
        flash("Cannot delete the last administrator.", "danger")
        return redirect(url_for('admin.users'))
    # Logic condition 3: Prevent deleting the last user in the database
    if User.query.count() == 1:
        flash("Cannot delete the last user in the database.", "danger")
        return redirect(url_for('admin.users'))
        
    if user.image_file != 'default.png':
        delete_picture(user.image_file, "static/media/user_pics")
    db.session.delete(user)
    db.session.commit()
    flash('User and their associated data have been deleted!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/toggle_ban', methods=['POST'])
@login_required
@admin_required
def toggle_ban(user_id):
    user = User.query.get_or_404(user_id)
    # Logic condition: Prevent an admin from banning themselves
    if user.id == current_user.id:
        flash("You cannot ban or unban your own account.", "danger")
        return redirect(url_for('admin.users'))
    
    user.is_banned = not user.is_banned
    db.session.commit()
    flash(f"User {user.username} has been {'banned' if user.is_banned else 'unbanned'}.", 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(user=user)
    if form.validate_on_submit():
        user.fname = form.fname.data
        user.lname = form. lname.data
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('User has been updated!', 'success')
        return redirect(url_for('admin.users'))
    elif request.method == 'GET':
        form.fname.data = user.fname
        form.lname.data = user.lname
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        category = None
        # Logic to handle a new category creation
        if form.new_category_name.data:
            new_category = Category(name=form.new_category_name.data)
            db.session.add(new_category)
            db.session.commit()
            category = new_category
            # Use existing category if selected
        elif form.category.data:
            category = form.category.data
        product = Product(
            name=form.name.data,
            description=form.description.data,
            category=category,  
            price=form.price.data,
            stock=form.stock.data,
            user_id=current_user.id
        )
        if form.image.data:
            picture_file = save_picture(form.image.data, 'static/media/product_images')
            product.image_file = picture_file
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.category = form.category.data
        product.price = form.price.data
        product.stock = form.stock.data
        if form.image.data:
            picture_file = save_picture(form.image.data, 'static/media/product_images')
            product.image_file = picture_file
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('admin.products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.stock.data = product.stock
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.image_file != 'default.png':
        delete_picture(product.image_file, "static/media/product_images")
        
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)
@admin_bp.route('/order/<int:order_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    try:
        if order.status == 'Pending':
            # Decrement product stock when order is shipped
            for order_product in order.products:
                product = Product.query.get(order_product.product_id)
                if product:
                    product.stock -= order_product.quantity
            order.status = 'Shipped'
            flash(f'Order #{order.id} status has been changed to Shipped. Stock updated.', 'success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while updating order status and stock: {e}', 'danger')
        
    return redirect(url_for('admin.order_detail', order_id=order.id))

@admin_bp.route('/subscriptions')
@login_required
@admin_required
def subscriptions():
    subscribers = Newsletter.query.all()
    return render_template('admin/subscriptions.html', subscribers=subscribers)

@admin_bp.route('/subscriber/<int:subscriber_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subscriber(subscriber_id):
    subscriber = Newsletter.query.get_or_404(subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash('Subscriber has been deleted!', 'success')
    return redirect(url_for('admin.subscriptions'))
