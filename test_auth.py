import pytest
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    """홈 페이지 접근 테스트"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hyeyum' in response.data

def test_signup(client, app):
    """회원가입 기능 테스트"""
    response = client.post('/signup', data={
        'username': 'testuser',
        'name': 'Test User',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.name == 'Test User'

def test_login_logout(client, app):
    """로그인 및 로그아웃 기능 테스트"""
    # 먼저 사용자 생성
    with app.app_context():
        user = User(
            username='loginuser',
            name='Login User',
            password=generate_password_hash('password123', method='pbkdf2:sha256')
        )
        db.session.add(user)
        db.session.commit()

    # 로그인
    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert b'Login User' in response.data
    
    # 로그아웃
    response = client.get('/logout', follow_redirects=True)
    assert b'\xeb\xa1\x9c\xea\xb7\xb8\xec\x9d\xb8' in response.data # '로그인' in Korean UTF-8

def test_admin_access(client, app):
    """관리자 권한 접근 제어 테스트"""
    # 일반 사용자 생성 및 로그인
    with app.app_context():
        user = User(
            username='normaluser',
            name='Normal User',
            password=generate_password_hash('pass', method='pbkdf2:sha256'),
            is_admin=False
        )
        admin = User(
            username='adminuser',
            name='Admin User',
            password=generate_password_hash('pass', method='pbkdf2:sha256'),
            is_admin=True
        )
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()

    # 일반 사용자로 관리자 페이지 접근 시도 (403 예상)
    client.post('/login', data={'username': 'normaluser', 'password': 'pass'})
    response = client.get('/admin')
    assert response.status_code == 403

    # 로그아웃 후 관리자로 로그인하여 접근 시도 (200 예상)
    client.get('/logout')
    client.post('/login', data={'username': 'adminuser', 'password': 'pass'})
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'ADMIN ONLY' in response.data
