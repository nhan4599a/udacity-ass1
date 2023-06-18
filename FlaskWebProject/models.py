from datetime import datetime
from FlaskWebProject import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
from flask import flash
import uuid
from enum import Enum
from FlaskWebProject.helper import get_form_values, parse_to_bool

blob_container = app.config['BLOB_CONTAINER']
blob_service_client = BlobServiceClient.from_connection_string(app.config['BLOB_STORAGE_ACCOUNT_URL'])
blob_container_client = blob_service_client.get_container_client(blob_container)


class UserProvider(Enum):
    INTERNAL = 0
    MICROSOFT = 1

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.UUID, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    #default password hashing is return 102 character in result
    password_hash = db.Column(db.String(102))
    is_external_user = db.Column(db.Boolean)
    provider = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def init_user(username, password=None, provider=UserProvider.INTERNAL):
        user = User()
        user.id = uuid.uuid4()
        user.username = username
        is_external_user = provider != UserProvider.INTERNAL

        if (not is_external_user and not password):
            raise Exception('password cannot be empty for internal user')
        if (is_external_user and password):
            raise Exception('Password cannot be set for external user')
        if (password):
            user.set_password(password)
        user.provider = provider.value
        user.is_external_user = is_external_user
        return user

@login.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.UUID, primary_key=True)
    title = db.Column(db.String(150))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(75))
    body = db.Column(db.String(800))
    image_path = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.UUID, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def save_changes(self, form, file, userId, new=False):
        data = get_form_values(form)
        self.id = self.id or uuid.uuid4()
        self.title = data['title']
        self.subtitle = data['subtitle']
        self.author = data['author']
        self.body = data['body']
        self.user_id = userId

        should_delete_blob = parse_to_bool(data['should_delete_blob'])

        if file:
            filename = secure_filename(self.image_path if self.image_path else file.filename)
            blob_client = blob_container_client.get_blob_client(filename)
            try:
                with file.stream as data:
                    blob_client.upload_blob(data, overwrite=True)
            except Exception:
                flash(Exception)
            self.image_path = filename
        elif should_delete_blob:
            blob_client = blob_container_client.get_blob_client(self.image_path)
            blob_client.delete_blob()
            self.image_path = None
        if new:
            db.session.add(self)
        db.session.commit()