from flask import Flask
from models import db, User, Post
from werkzeug.security import generate_password_hash
import os

def init_db():
    app = Flask(__name__)
    # Ensure instance folder exists
    instance_path = os.path.join(os.getcwd(), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(instance_path, 'site.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # 데이터베이스 초기화 (기존 테이블 삭제 후 생성)
        db.drop_all()
        db.create_all()
        
        # 관리자 계정 생성
        admin_username = 'admin'
        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(
                username=admin_username,
                name='관리자',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user created: {admin_username}")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
