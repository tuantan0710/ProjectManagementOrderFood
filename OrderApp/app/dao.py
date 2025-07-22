from app.models import DanhMucMonAn, MonAn, User, NhaHang, EnumRole,DeliveryAddress
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

def add_user(name, username, password, email, avt=None):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

    u = User(name=name, username=username, password=password, email=email)
    if avt:
        res = cloudinary.uploader.upload(avt)
        u.avt = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

def add_nha_hang(name, username, password, email, adress, MST, gio_mo_cua, gio_dong_cua, avt=None):
    password_hashed = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

    nh = NhaHang(
        name=name,
        username=username,
        password=password_hashed,
        email=email,
        adress=adress,
        MST=MST,
        gio_mo_cua=gio_mo_cua,
        gio_dong_cua=gio_dong_cua,
        role=EnumRole.nhaHang
    )

    if avt:
        res = cloudinary.uploader.upload(avt)
        nh.avt = res.get('secure_url')

    db.session.add(nh)
    db.session.commit()
def load_foods(keyword=None):
    query = MonAn.query

    if keyword:
        keyword = f"%{keyword.strip()}%"
        query = query.filter(MonAn.name.ilike(keyword))

    return query.all()


def load_nha_hang(keyword=None):
    query = NhaHang.query

    if keyword:
        keyword = f"%{keyword.strip()}%"
        query = query.filter((NhaHang.name.ilike(keyword)) | (NhaHang.username.ilike(keyword)))

    return query.all()
def count_cart(cart):
    total_quantity,total_amount=0,0
    if cart:
        for c in cart.values():
            total_quantity+=c['quantity']
            total_amount+=c['quantity']*c['gia']
    return {
        "total_amount":total_amount,
        "total_quantity":total_quantity
    }
def get_user_addresses(user_id):
    return db.session.query(DeliveryAddress).filter(DeliveryAddress.user_id == user_id).all()