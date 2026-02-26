from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from models import Post, User, get_now_kst, Log
from firebase_config import get_db, firestore_module
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    db_fs = get_db()
    if not db_fs:
        return render_template('index.html', posts=[])
    
    # [FIX] 관리자 계정이 없으면 여기서 한 번만 생성 (마스터 프로세스 충돌 방지용)
    try:
        admin_username = 'admin'
        users_ref = db_fs.collection('users')
        # 이미 있는지 확인
        if not next(users_ref.where('username', '==', admin_username).limit(1).stream(), None):
            admin_data = {
                'username': admin_username,
                'name': '관리자',
                'password': generate_password_hash('admin123', method='pbkdf2:sha256'),
                'is_admin': True,
                'created_at': get_now_kst()
            }
            db_fs.collection('users').add(admin_data)
            print(f"Admin user created in Firestore: {admin_username}")
    except Exception as e:
        print(f"Error during admin user check/creation: {e}")

    try:
        posts_ref = db_fs.collection('posts')
        query = posts_ref.order_by('date_posted', direction=firestore_module.Query.DESCENDING).stream()
        posts = [Post.from_dict(doc.to_dict(), doc.id) for doc in query]
    except Exception as e:
        print(f"Error fetching posts: {e}")
        posts = []
        
    return render_template('index.html', posts=posts)

@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    db_fs = get_db()
    users = []
    logs = []
    if db_fs:
        # 회원 목록 가져오기
        try:
            users_ref = db_fs.collection('users')
            query_users = users_ref.order_by('created_at', direction=firestore_module.Query.DESCENDING).stream()
            users = [User.from_dict(doc.to_dict(), doc.id) for doc in query_users]
        except Exception as e:
            print(f"Error fetching users for admin: {e}")
            try:
                users = [User.from_dict(doc.to_dict(), doc.id) for doc in users_ref.stream()]
            except:
                users = []

        # 로그 목록 가져오기 (최신 10개)
        try:
            logs_ref = db_fs.collection('logs')
            query_logs = logs_ref.order_by('timestamp', direction=firestore_module.Query.DESCENDING).limit(10).stream()
            logs = [Log.from_dict(doc.to_dict(), doc.id) for doc in query_logs]
        except Exception as e:
            print(f"Error fetching logs for admin: {e}")
            try:
                # 인덱스 미생성 시 정렬 없이 가져오기
                logs = [Log.from_dict(doc.to_dict(), doc.id) for doc in logs_ref.limit(10).stream()]
            except:
                logs = []
                
    return render_template('admin.html', users=users, logs=logs)

@main.route('/board')
def board():
    return redirect(url_for('main.index'))

@main.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    db_fs = get_db()
    if not db_fs:
        flash('데이터베이스 연동 설정이 필요합니다.')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.')
        else:
            new_post_data = {
                'title': title,
                'content': content,
                'author_id': current_user.id,
                'author_name': current_user.name,
                'date_posted': get_now_kst()
            }
            post_ref = db_fs.collection('posts').add(new_post_data)
            
            # [LOG] 게시글 작성 기록
            try:
                db_fs.collection('logs').add({
                    'action': '게시글 작성',
                    'user_id': current_user.id,
                    'user_name': current_user.name,
                    'details': f"제목: '{title}'",
                    'timestamp': get_now_kst()
                })
            except Exception as e:
                print(f"Error logging new post: {e}")

            flash('게시글이 등록되었습니다!')
            return redirect(url_for('main.index'))
    return render_template('post_form.html', title='새 글 작성', legend='새 글 작성')

@main.route('/post/<string:post_id>')
def post_detail(post_id):
    db_fs = get_db()
    if not db_fs:
        abort(404)
    
    post_doc = db_fs.collection('posts').document(post_id).get()
    if not post_doc.exists:
        abort(404)
    
    post = Post.from_dict(post_doc.to_dict(), post_doc.id)
    return render_template('post_detail.html', post=post)

@main.route('/post/<string:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    db_fs = get_db()
    if not db_fs:
        abort(404)
        
    post_doc = db_fs.collection('posts').document(post_id).get()
    if not post_doc.exists:
        abort(404)
    
    post_data = post_doc.to_dict()
    # 작성자 본인이거나 관리자인 경우에만 수정 가능
    if post_data.get('author_id') != current_user.id and not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        updated_data = {
            'title': request.form.get('title'),
            'content': request.form.get('content')
        }
        db_fs.collection('posts').document(post_id).update(updated_data)
        
        # [LOG] 게시글 수정 기록
        try:
            db_fs.collection('logs').add({
                'action': '게시글 수정',
                'user_id': current_user.id,
                'user_name': current_user.name,
                'details': f"제목: '{updated_data['title']}' (ID: {post_id})",
                'timestamp': get_now_kst()
            })
        except Exception as e:
            print(f"Error logging update post: {e}")

        flash('게시글이 수정되었습니다!')
        return redirect(url_for('main.post_detail', post_id=post_id))
    
    post = Post.from_dict(post_data, post_doc.id)
    return render_template('post_form.html', title='글 수정', legend='글 수정', post=post)

@main.route('/post/<string:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    db_fs = get_db()
    if not db_fs:
        abort(404)
        
    post_doc = db_fs.collection('posts').document(post_id).get()
    if not post_doc.exists:
        abort(404)
    
    post_data = post_doc.to_dict()
    # 작성자 본인이거나 관리자인 경우에만 삭제 가능
    if post_data.get('author_id') != current_user.id and not current_user.is_admin:
        abort(403)
    
    db_fs.collection('posts').document(post_id).delete()
    
    # [LOG] 게시글 삭제 기록
    try:
        db_fs.collection('logs').add({
            'action': '게시글 삭제',
            'user_id': current_user.id,
            'user_name': current_user.name,
            'details': f"제목: '{post_data.get('title')}' (ID: {post_id})",
            'timestamp': get_now_kst()
        })
    except Exception as e:
        print(f"Error logging delete post: {e}")

    flash('게시글이 삭제되었습니다!')
    return redirect(url_for('main.index'))
