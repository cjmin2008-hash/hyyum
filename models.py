from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

# KST (UTC+9) 설정
KST = timezone(timedelta(hours=9))

def get_now_kst():
    """현재 한국 표준시를 반환합니다."""
    return datetime.now(KST)

def to_kst(dt):
    """datetime 객체를 KST로 변환합니다."""
    if not dt:
        return dt
    if dt.tzinfo is None:
        # naive datetime인 경우 UTC로 가정하고 KST로 변환
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST)

class User(UserMixin):
    def __init__(self, id, username, name, password, is_admin=False, created_at=None):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
        self.is_admin = is_admin
        self.created_at = created_at or get_now_kst()

    @staticmethod
    def from_dict(source, id):
        return User(
            id=id,
            username=source.get('username'),
            name=source.get('name'),
            password=source.get('password'),
            is_admin=source.get('is_admin', False),
            created_at=to_kst(source.get('created_at'))
        )

    def to_dict(self):
        return {
            'username': self.username,
            'name': self.name,
            'password': self.password,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }

class Post:
    def __init__(self, id, title, content, author_id, author_name, date_posted=None, is_pinned=False):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.author_name = author_name
        self.date_posted = date_posted or get_now_kst()
        self.is_pinned = is_pinned

    @staticmethod
    def from_dict(source, id):
        return Post(
            id=id,
            title=source.get('title'),
            content=source.get('content'),
            author_id=source.get('author_id'),
            author_name=source.get('author_name'),
            date_posted=to_kst(source.get('date_posted')),
            is_pinned=source.get('is_pinned', False)
        )

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'date_posted': self.date_posted,
            'is_pinned': self.is_pinned
        }

class Log:
    def __init__(self, id, action, user_id, user_name, details, timestamp=None):
        self.id = id
        self.action = action
        self.user_id = user_id
        self.user_name = user_name
        self.details = details
        self.timestamp = timestamp or get_now_kst()

    @staticmethod
    def from_dict(source, id):
        return Log(
            id=id,
            action=source.get('action'),
            user_id=source.get('user_id'),
            user_name=source.get('user_name'),
            details=source.get('details'),
            timestamp=to_kst(source.get('timestamp'))
        )

    def to_dict(self):
        return {
            'action': self.action,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'details': self.details,
            'timestamp': self.timestamp
        }
