import os
import secrets

from app import app, db, mail 
from flask_mail import Message
from flask import  url_for



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request",
        sender=app.config['MAIL_USERNAME'],
        recipients=[user.email]
    )
    
    # Plain text body for clients that don't support HTML
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request, please ignore this email and no changes will be made."""

    # HTML body with a button link
    msg.html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Password Reset Request</h2>
        <p>Hello {user.fname},</p>
        <p>A password reset request has been made for your account. If you made this request, click the button below to reset your password.</p>
        <a href="{url_for('reset_password', token=token, _external=True)}" style="
            display: inline-block; 
            padding: 12px 24px; 
            font-size: 16px; 
            color: #ffffff; 
            background-color: #007bff; 
            border-radius: 5px; 
            text-decoration: none; 
            font-weight: bold;
        ">Reset Password</a>
        <p>If you did not make this request, you can safely ignore this email.</p>
        <p>Thank you,<br>
        Your Website Team</p>
    </div>
    """
    mail.send(msg)

def send_order_notification_email(order):
    # Email to customer
    customer_msg = Message(
        f"Your Order #{order.id} has been placed!",
        sender=app.config['MAIL_USERNAME'],
        recipients=[order.customer.email]
    )
    customer_msg.body = f"""
    Thank you for your order!

    Order ID: {order.id}
    Total Amount: ${order.total_amount:.2f}
    """
    customer_msg.html = f"""
    <h2>Thank you for your order!</h2>
    <p><strong>Order ID:</strong> {order.id}</p>
    <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>
    <p>We'll notify you when your order has shipped.</p>
    """
    mail.send(customer_msg)

    # Email to admin
    admin_msg = Message(
        "New Order Received",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['ADMIN_EMAIL']]
    )
    admin_msg.body = f"""
    A new order has been placed.

    Order ID: {order.id}
    Customer: {order.customer.username}
    Total Amount: ${order.total_amount:.2f}
    """
    admin_msg.html = f"""
    <h2>New Order Received</h2>
    <p><strong>Order ID:</strong> {order.id}</p>
    <p><strong>Customer:</strong> {order.customer.username}</p>
    <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>
    <p><strong>Products:</strong></p>
    <ul>
        {''.join(f'<li>{p.product.name} (x{p.quantity})</li>' for p in order.products)}
    </ul>
    """
    mail.send(admin_msg)
