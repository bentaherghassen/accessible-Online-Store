"""
    CODE FOR TEST ONLY
"""    

from app import app, db
from app.models import User

with app.app_context():
    # Find the user by their email or username
    user = User.query.filter_by(email='email@email.com').first()
    if user:
        # Set the is_admin attribute to True
        user.is_admin = True
        db.session.commit()
        print(f"User {user.username} is now an admin.")
    else:
        print("User not found.")