from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from firebase_config import db_fs
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    if not db_fs:
        flash('데이터베이스 연동 설정이 필요합니다.')
        return redirect(url_for('auth.login'))

    # Firestore에서 사용자 조회
    users_ref = db_fs.collection('users')
    query = users_ref.where('username', '==', username).limit(1).stream()
    user_doc = next(query, None)

    if not user_doc:
        flash('로그인 정보가 올바르지 않습니다.')
        return redirect(url_for('auth.login'))

    user_data = user_doc.to_dict()
    if not check_password_hash(user_data.get('password'), password):
        flash('로그인 정보가 올바르지 않습니다.')
        return redirect(url_for('auth.login'))

    user = User.from_dict(user_data, user_doc.id)
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('password')

    if not db_fs:
        flash('데이터베이스 연동 설정이 필요합니다.')
        return redirect(url_for('auth.signup'))

    # 중복 확인
    users_ref = db_fs.collection('users')
    query = users_ref.where('username', '==', username).limit(1).stream()
    if next(query, None):
        flash('이미 존재하는 아이디입니다.')
        return redirect(url_for('auth.signup'))

    # 사용자 생성
    new_user_data = {
        'username': username,
        'name': name,
        'password': generate_password_hash(password, method='pbkdf2:sha256'),
        'is_admin': False,
        'created_at': datetime.utcnow()
    }
    
    db_fs.collection('users').add(new_user_data)
    flash('회원가입이 완료되었습니다! 로그인해주세요.')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
