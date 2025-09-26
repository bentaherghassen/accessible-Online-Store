from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config) # Use Config class directly

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

from app.blueprints.auth import auth_bp
from app.blueprints.main import main_bp
from app.blueprints.products import products_bp
from app.blueprints.orders import orders_bp
from app.blueprints.errors import errors_bp
from app.blueprints.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(products_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(admin_bp)



from app import context_processors 