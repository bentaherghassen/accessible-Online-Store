from app import app
from flask import session
from app.forms import NewsletterForm
from datetime import datetime

@app.context_processor
def inject_global_data():
    cart_count = 0
    if "cart" in session and session["cart"]:
        cart_count = sum(item["quantity"] for item in session["cart"])

    # Store Open/Closed status
    now = datetime.now().time()
    store_open = 9 <= now.hour < 22
    store_status = "Open" if store_open else "Closed"
    store_status_color = "green" if store_open else "red"

    return dict(
        cart_count=cart_count,
        newsletter_form=NewsletterForm(),
        store_status=store_status,
        store_status_color=store_status_color
    )