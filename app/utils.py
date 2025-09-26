import os
import secrets
from PIL import Image
from flask import current_app
from app import app,db,bcrypt
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Order,User

def save_picture(form_picture, path, output_size=None):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext

    # Create the full path to the directory
    picture_dir = os.path.join(app.root_path, path)
    
    # Create the directory if it doesn't exist
    os.makedirs(picture_dir, exist_ok=True)
    
    picture_path = os.path.join(picture_dir, picture_name)
    
    i = Image.open(form_picture)
    if output_size:
        i.thumbnail(output_size)
    i.save(picture_path)
    return picture_name

def delete_picture(picture_name, path):
    """
    Deletes a picture from the filesystem, if it exists.

    Args:
        picture_name (str): The name of the picture file to delete.
        path (str): The directory path where the picture is located, relative to app.root_path.
    """
    picture_path = os.path.join(app.root_path, path, picture_name)
    
    # Check if the file exists before attempting to delete it
    if os.path.exists(picture_path):
        try:
            os.remove(picture_path)
        except OSError as e:
            # Handle permissions or other OS-level errors
            print(f"Error deleting file {picture_path}: {e}")
            
def get_client_of_the_week():
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    top_client = db.session.query(
        User,
        func.sum(Order.total_amount).label('total_spent')
    ).join(Order, User.id == Order.user_id)\
    .filter(Order.order_date >= start_of_week)\
    .filter(Order.order_date <= end_of_week)\
    .group_by(User)\
    .order_by(func.sum(Order.total_amount).desc())\
    .first()

    return top_client[0] if top_client else None
