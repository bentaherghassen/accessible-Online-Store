"""
    CODE FOR TEST ONLY
"""    

from app import app, db, bcrypt
from app.models import User, Product, Category, Order, Cart, CartItem, OrderProduct, Review, Newsletter
from datetime import datetime

def create_user():
    print("--- Creating a new User ---")
    fname = input("Enter first name: ")
    lname = input("Enter last name: ")
    username = input("Enter username: ")
    email = input("Enter email: ")
    plain_password = input("Enter password: ")
    hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
    gender = input("Enter gender: ")
    phone_number = input("Enter phone number (optional): ")
    home_address = input("Enter home address (optional): ")
    is_admin = input("Is this user an admin? (yes/no): ").lower() == 'yes'
    is_banned = input("Is this user banned? (yes/no): ").lower() == 'yes'
    
    new_user = User(
        fname=fname,
        lname=lname,
        username=username,
        email=email,
        password=hashed_password,
        gender=gender,
        phone_number=phone_number or None,
        home_address=home_address or None,
        is_admin=is_admin,
        is_banned=is_banned
    )
    db.session.add(new_user)
    db.session.commit()
    print(f"User '{new_user.username}' created successfully!")
    return new_user

def create_product():
    print("--- Creating a new Product ---")
    name = input("Enter product name: ")
    description = input("Enter product description: ")
    price = float(input("Enter price: "))
    stock = int(input("Enter stock quantity: "))
    image_file = input("Enter image file name (optional, defaults to 'default.png'): ")
    category_id = int(input("Enter category ID: "))
    user_id = int(input("Enter the user ID of the uploader: "))

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_file=image_file or 'default.png',
        category_id=category_id,
        user_id=user_id
    )
    db.session.add(new_product)
    db.session.commit()
    print(f"Product '{new_product.name}' created successfully!")
    return new_product

def create_category():
    print("--- Creating a new Category ---")
    name = input("Enter category name: ")
    
    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    print(f"Category '{new_category.name}' created successfully!")
    return new_category

def create_order():
    print("--- Creating a new Order ---")
    user_id = int(input("Enter user ID for the order: "))
    total_amount = float(input("Enter total amount: "))
    status = input("Enter order status (e.g., 'Pending', 'Shipped', 'Delivered'): ")
    
    new_order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=status
    )
    db.session.add(new_order)
    db.session.commit()
    print(f"Order created successfully with ID: {new_order.id}")
    return new_order

def create_order_product():
    print("--- Adding a Product to an Order ---")
    order_id = int(input("Enter order ID: "))
    product_id = int(input("Enter product ID: "))
    quantity = int(input("Enter quantity: "))

    new_order_product = OrderProduct(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(new_order_product)
    db.session.commit()
    print("Product added to order successfully!")
    return new_order_product

def create_cart_item():
    print("--- Adding an Item to a Cart ---")
    user_id = int(input("Enter user ID to find their cart: "))
    product_id = int(input("Enter product ID to add to cart: "))
    quantity = int(input("Enter quantity: "))
    
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        print("Cart not found for this user. Creating a new cart.")
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    new_cart_item = CartItem(
        cart_id=cart.id,
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(new_cart_item)
    db.session.commit()
    print("Cart item added successfully!")
    return new_cart_item

def create_review():
    print("--- Creating a new Review ---")
    rating = int(input("Enter rating (1-5): "))
    text = input("Enter review text: ")
    user_id = int(input("Enter user ID of the reviewer: "))
    product_id = int(input("Enter product ID being reviewed: "))

    new_review = Review(
        rating=rating,
        text=text,
        user_id=user_id,
        product_id=product_id
    )
    db.session.add(new_review)
    db.session.commit()
    print("Review created successfully!")
    return new_review

def create_newsletter_subscriber():
    print("--- Adding a new Newsletter Subscriber ---")
    email = input("Enter subscriber email: ")
    
    new_subscriber = Newsletter(email=email)
    db.session.add(new_subscriber)
    db.session.commit()
    print("Newsletter subscription added successfully!")
    return new_subscriber

def main():
    with app.app_context():
        # Ensure tables are created before populating
        print("Ensuring database tables exist...")
        db.create_all()
        print("Database tables are ready.")

        while True:
            print("\n--- Data Creation Menu ---")
            print("1. Create User")
            print("2. Create Product")
            print("3. Create Category")
            print("4. Create Order")
            print("5. Add Product to Order")
            print("6. Add Item to Cart")
            print("7. Create Review")
            print("8. Add Newsletter Subscriber")
            print("9. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                create_user()
            elif choice == '2':
                create_product()
            elif choice == '3':
                create_category()
            elif choice == '4':
                create_order()
            elif choice == '5':
                create_order_product()
            elif choice == '6':
                create_cart_item()
            elif choice == '7':
                create_review()
            elif choice == '8':
                create_newsletter_subscriber()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()