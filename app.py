import os
import sys
from flask import Flask
from models import User
from flask_login import LoginManager
from firebase_config import get_db

print(f"Current Python Version: {sys.version}")

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev-secret-key-12345'
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_fs = get_db()
        if not db_fs:
            return None
        user_doc = db_fs.collection('users').document(user_id).get()
        if user_doc.exists:
            return User.from_dict(user_doc.to_dict(), user_doc.id)
        return None

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
