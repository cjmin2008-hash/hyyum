from flask_login import UserMixin
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, name, password, is_admin=False, created_at=None):
        self.id = id
        self.username = username
        self.name = name
        self.password = password
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(source, id):
        return User(
            id=id,
            username=source.get('username'),
            name=source.get('name'),
            password=source.get('password'),
            is_admin=source.get('is_admin', False),
            created_at=source.get('created_at')
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
    def __init__(self, id, title, content, author_id, author_name, date_posted=None):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.author_name = author_name
        self.date_posted = date_posted or datetime.utcnow()

    @staticmethod
    def from_dict(source, id):
        return Post(
            id=id,
            title=source.get('title'),
            content=source.get('content'),
            author_id=source.get('author_id'),
            author_name=source.get('author_name'),
            date_posted=source.get('date_posted')
        )

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'date_posted': self.date_posted
        }
