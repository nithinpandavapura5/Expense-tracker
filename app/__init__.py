from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245' # Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        
        # Create default categories if they don't exist
        from app.models import Category
        if Category.query.count() == 0:
            categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Rent', 'Other']
            for name in categories:
                db.session.add(Category(name=name))
            db.session.commit()
        
    return app
