from flask import render_template, request, jsonify, Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Product, Cart, CartItem, Order,OrderProduct
from app.hundlers import send_order_notification_email
from decimal import Decimal

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/cart/count", methods=["GET"])
@login_required
def cart_count():
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart:
            count = sum(item.quantity for item in cart.items)
            return jsonify({"cart_count": count})
    return jsonify({"cart_count": 0})

@orders_bp.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = request.json.get("product_id")
    quantity = request.json.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart = current_user.cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += int(quantity)
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=int(quantity))
        db.session.add(cart_item)

    db.session.commit()

    cart_count = sum(item.quantity for item in cart.items)
    flash("Product added to cart!", "success")
    return jsonify({"cart_count": cart_count, "message": "Product added to cart!"})

@orders_bp.route("/cart")
@login_required
def cart():
    cart = current_user.cart
    if not cart:
        return render_template("cart.html", cart_items=[], subtotal_price=0, total_items=0, shipping_cost=0, total_price=0)

    # Pass the list of CartItem objects directly to the template
    cart_items = cart.items
    
    subtotal_price = 0
    total_items = 0
    shipping_cost = 7

    for item in cart_items:
        # Check if the product relationship exists
        if item.product:
            subtotal_price += float(item.product.price) * item.quantity
            total_items += item.quantity
        else:
            # Handle cases where a product might be missing, e.g., removed from the database
            # You might want to remove this item from the cart or show a warning.
            # For this fix, i'll just skip it.
            pass

    total_price = subtotal_price + shipping_cost

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal_price=subtotal_price,
        total_items=total_items,
        shipping_cost=shipping_cost,
        total_price=total_price,
    )
@orders_bp.route("/update_cart_item/<int:item_id>", methods=["POST"])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    # Security check to ensure the current user owns the cart item
    if cart_item.cart.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # I used request.form to get data from the HTML form submission
    quantity_str = request.form.get("quantity")
    
    if quantity_str is not None:
        try:
            quantity = int(quantity_str)
            if quantity > 0:
                cart_item.quantity = quantity
                db.session.commit()
                flash("Cart item updated successfully!", "success")
            else:
                flash("Quantity must be at least 1.", "danger")
        except ValueError:
            flash("Invalid quantity value.", "danger")
    
    return redirect(url_for('orders.cart'))

@orders_bp.route("/remove_from_cart/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(cart_item)
    db.session.commit()
    flash("Product removed from cart!", "success")

    return redirect(url_for('orders.cart'))


@orders_bp.route("/clear_cart", methods=["POST"])
@login_required
def clear_cart():
    cart = current_user.cart
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        flash("Your cart has been cleared.", "success")
    return redirect(url_for('orders.cart'))


""" @orders_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    # retrieves the shopping cart associated with the currently logged-in user. 
    cart = current_user.cart
    # Check if the cart alredy exist
    if not cart or not cart.items:
        flash("Your cart is empty.", "info")
        return redirect(url_for('orders.cart'))

# Get the total amount
    total_amount = 0
    for item in cart.items:
        product = Product.query.get(item.product_id)
        total_amount += product.price * item.quantity
# add order to db
    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.commit()

# add order product to db
    for item in cart.items:
        order_product = OrderProduct(order_id=order.id, product_id=item.product_id, quantity=item.quantity)
        db.session.add(order_product)
        # Delete cart item
        db.session.delete(item)

    db.session.commit()

    #send_order_notification_email(order)

    flash("Your order has been placed successfully!", "success")
    #return redirect(url_for('main.home'))
    return redirect(url_for('orders.order_confirmation', order_id=order.id)) """


@orders_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = current_user.cart
    if not cart or not cart.items:
        flash("Your cart is empty.", "info")
        return redirect(url_for('orders.cart'))

    #  dictionary to aggregate quantities of identical products
    aggregated_items = {}
    for item in cart.items:
        product = Product.query.get(item.product_id)
        if product.id not in aggregated_items:
            aggregated_items[product.id] = {
                'quantity': item.quantity,
                'price': product.price
            }
        else:
            aggregated_items[product.id]['quantity'] += item.quantity

    total_amount = Decimal('0.00')
    for item_id, data in aggregated_items.items():
        total_amount += Decimal(str(data['price'])) * data['quantity']

    order = Order(user_id=current_user.id, total_amount=total_amount)
    db.session.add(order)
    db.session.flush() # Flush to get the order ID before committing

    for product_id, data in aggregated_items.items():
        order_product = OrderProduct(
            order_id=order.id, 
            product_id=product_id, 
            quantity=data['quantity']
        )
        db.session.add(order_product)

    # Delete all items from the cart after they've been successfully moved to the order
    CartItem.query.filter_by(cart_id=cart.id).delete()
    
    db.session.commit()

    send_order_notification_email(order)

    flash("Your order has been placed successfully!", "success")
    return redirect(url_for('orders.order_confirmation', order_id=order.id))


@orders_bp.route("/order_confirmation/<int:order_id>")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    # Security check: Ensure the current user is the owner of this order
    if order.user_id != current_user.id:
        flash("You do not have permission to view this order.", "danger")
        return redirect(url_for('main.home'))

    # The order_product_association is a many-to-many relationship.
    # We can get the order items through the OrderProduct model
    order_items = OrderProduct.query.filter_by(order_id=order_id).all()
    
    # Define shipping cost and calculate final total
    shipping_cost = 7.00
    final_total = float(order.total_amount) + shipping_cost

    return render_template(
        "order_confirmation.html",
        order=order,
        order_items=order_items,
        shipping_cost=shipping_cost,
        final_total=final_total
    )
    
@orders_bp.route("/order_history")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', orders=orders, title = 'Order History ')