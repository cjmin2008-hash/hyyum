from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from models import Post
from firebase_config import get_db, firestore_module
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    db_fs = get_db()
    if not db_fs:
        return render_template('index.html', posts=[])
    
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
    return render_template('admin.html')

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
                'date_posted': datetime.utcnow()
            }
            db_fs.collection('posts').add(new_post_data)
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
    flash('게시글이 삭제되었습니다!')
    return redirect(url_for('main.index'))
