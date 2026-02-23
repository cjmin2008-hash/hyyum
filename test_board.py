import pytest
from app import create_app
from models import db, User, Post
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

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_board_crud(client, app):
    """게시판 CRUD 기본 기능 테스트"""
    # 1. 사용자 생성 및 로그인
    with app.app_context():
        user = User(username='writer', name='Writer', password=generate_password_hash('pass', method='pbkdf2:sha256'))
        db.session.add(user)
        db.session.commit()
    
    login(client, 'writer', 'pass')
    
    # 2. 글 작성
    response = client.post('/post/new', data=dict(
        title='Test Post',
        content='This is a test content'
    ), follow_redirects=True)
    assert b'Test Post' in response.data
    
    # 홈 화면에서 글이 보이는지 확인 (추가된 검증)
    response = client.get('/', follow_redirects=True)
    assert b'Test Post' in response.data
    
    # 3. 글 수정
    with app.app_context():
        post = Post.query.filter_by(title='Test Post').first()
        post_id = post.id
        
    response = client.post(f'/post/{post_id}/update', data=dict(
        title='Updated Post',
        content='Updated content'
    ), follow_redirects=True)
    assert b'Updated Post' in response.data
    
    # 4. 글 삭제
    response = client.post(f'/post/{post_id}/delete', follow_redirects=True)
    assert b'\xec\x82\xad\xec\xa0\x9c\xeb\x90\x98\xec\x97\x88\xec\x8a\xb5\xeb\x8b\x88\xeb\x8b\xa4' in response.data # '삭제되었습니다'

def test_admin_authority(client, app):
    """관리자의 타인 게시글 관리 권한 테스트"""
    with app.app_context():
        user = User(username='user', name='User', password=generate_password_hash('pass', method='pbkdf2:sha256'))
        admin = User(username='admin_boss', name='Admin', password=generate_password_hash('pass', method='pbkdf2:sha256'), is_admin=True)
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()
        
        post = Post(title='User Post', content='Secret', author=user)
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    # 1. 관리자로 로그인
    login(client, 'admin_boss', 'pass')
    
    # 2. 다른 사용자의 글 수정 시도
    response = client.post(f'/post/{post_id}/update', data=dict(
        title='Admin Hijacked',
        content='I am admin'
    ), follow_redirects=True)
    assert b'Admin Hijacked' in response.data
    
    # 3. 다른 사용자의 글 삭제 시도
    response = client.post(f'/post/{post_id}/delete', follow_redirects=True)
    assert b'\xec\x82\xad\xec\xa0\x9c\xeb\x90\x98\xec\x97\x88\xec\x8a\xb5\xeb\x8b\x88\xeb\x8b\xa4' in response.data
