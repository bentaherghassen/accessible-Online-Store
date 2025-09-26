from flask import render_template, request, Blueprint, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Product, Category, User, Review

products_bp = Blueprint('products', __name__)

@products_bp.route("/products")
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'date_desc')

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    else: # Default to date (id)
        query = query.order_by(Product.id.desc())

    per_page = 16
    products = query.paginate(page=page, per_page=per_page)
    categories = Category.query.all()
    return render_template("products.html", products=products, categories=categories, sort_by=sort_by,title = "PRODUCTS")

@products_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

@products_bp.route("/products/user/<int:user_id>")
def user_products(user_id):
    user = User.query.get_or_404(user_id)
    products = Product.query.filter_by(uploader=user).all()
    return render_template("user_products.html", products=products, user=user)

@products_bp.route("/products/search", methods=["POST"])
def search_products():
    search_term = request.form.get("search", "")
    if search_term:
        products = Product.query.filter(Product.name.ilike(f"%{search_term}%")).all()
    else:
        products = Product.query.all()
    return render_template("_search_results.html", products=products)

@products_bp.route("/product/<int:product_id>/add_review", methods=["POST"])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    rating = data.get('rating')
    text = data.get('text')

    if not rating or not text:
        return jsonify({"error": "Rating and text are required."}), 400

    review = Review(
        rating=rating,
        text=text,
        user_id=current_user.id,
        product_id=product.id
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({
        "id": review.id,
        "rating": review.rating,
        "text": review.text,
        "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "author": {
            "username": current_user.username
        }
    }), 201
