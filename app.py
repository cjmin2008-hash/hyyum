import os
from flask import Flask
from models import User
from flask_login import LoginManager
from firebase_config import db_fs

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev-secret-key-12345'
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
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

    with app.app_context():
        if db_fs:
            print("Firebase Firestore connected.")
            # 초기 관리자 계정 Firestore 확인/생성
            from werkzeug.security import generate_password_hash
            from datetime import datetime
            admin_username = 'admin'
            query = db_fs.collection('users').where('username', '==', admin_username).limit(1).stream()
            if not next(query, None):
                admin_data = {
                    'username': admin_username,
                    'name': 'Administrator',
                    'password': generate_password_hash('admin123', method='pbkdf2:sha256'),
                    'is_admin': True,
                    'created_at': datetime.utcnow()
                }
                db_fs.collection('users').add(admin_data)
                print(f"Admin user created in Firestore: {admin_username}")
        else:
            print("WARNING: Firebase not initialized. Application may not work properly.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
