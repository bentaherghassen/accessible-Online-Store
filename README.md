# Accessible Online Store

Below is a full-featured e-commerce website built with Flask , showcasing my skills in building **accessible , fully functional web applications**.
It includes a complete admin panel for managing users, products, orders, and newsletter subscriptions.

## Features

- **User Management:** Admins can add, edit, and delete users.
- **Product Management:** Admins can add, edit, and delete products.
- **Order Management:** Admins can view all orders and their details.
- **Subscription Management:** Admins can view and delete newsletter subscribers.
- **Shopping Cart:** Users can add products to their cart, update quantities, and remove items.
- **Checkout:** Users can place orders and receive email notifications.
- **User Authentication:** Users can register, log in, and reset their passwords.
- **User Profiles:** Users can view and update their profiles.

## Technologies Used

- **Backend:** Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Mail
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** SQLite

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bentaherghassen/accessible-Online-Store.git
    ```
2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Initialize the database:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
5.  **Run the application:**
    ```bash
    flask run
    ```

## Admin Panel

The admin panel is available at `/admin`. You can log in with your admin user credentials.

** First user is admin as default **
