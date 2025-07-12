from app.models import DanhMucMonAn, MonAn, User
import hashlib
import cloudinary.uploader
from app import app, db
def load_categories():
    return DanhMucMonAn.query.all()

def load_foods():
    return MonAn.query.all()

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()

def add_user(name, username, password, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()
