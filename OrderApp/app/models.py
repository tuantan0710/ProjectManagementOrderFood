from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from app import app, db
import hashlib
from flask_login import UserMixin

# ---------------- ENUM ----------------

class EnumRole(Enum):
    khachHang = "khachHang"
    nhaHang = "nhaHang"
    admin = "Admin"

class EnumStatus(Enum):
    cho = "Đang chờ"
    daXacNhan = "Đã xác nhận"
    daHuy = "Đã hủy"
    daGiao = "Đã giao cho vận chuyển"

# ---------------- USER + KẾ THỪA ----------------

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    avt = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(EnumRole), default=EnumRole.khachHang)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    danh_gia = db.relationship('DanhGia', backref='user', lazy=True)
    gio_hang = db.relationship('GioHang', backref='user', lazy=True)
    don_hang = db.relationship('DonHang', backref='khach_hang', lazy=True)

class NhaHang(User):
    __tablename__ = 'nhaHang'

    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    adress = db.Column(db.String(200))
    MST = db.Column(db.String(50))
    gio_mo_cua = db.Column(db.Time)
    gio_dong_cua = db.Column(db.Time)

    __mapper_args__ = {
        'polymorphic_identity': 'nhaHang',
    }

    don_hang = db.relationship('DonHang', backref='nha_hang', lazy=True)
    gio_hang = db.relationship('GioHang', backref='nha_hang', lazy=True)
    mon_an = db.relationship('MonAn', backref='nha_hang', lazy=True)

# ---------------- CÁC MODEL KHÁC ----------------

class DanhMucMonAn(db.Model):
    __tablename__ = 'danhMucMonAn'

    id = db.Column(db.Integer, primary_key=True)
    tenDanhMuc = db.Column(db.String(100), nullable=False)

    mon_an = db.relationship('MonAn', backref='danh_muc', lazy=True)

class MonAn(db.Model):
    __tablename__ = 'monAn'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chiTietMon = db.Column(db.Text)
    gia = db.Column(db.Float)
    img = db.Column(db.String(255))
    tinhTrang = db.Column(db.Boolean, default=True)
    idDanhMuc = db.Column(db.Integer, db.ForeignKey('danhMucMonAn.id'))
    idNhaHang = db.Column(db.Integer, db.ForeignKey('nhaHang.id'))

    chi_tiet_gio_hang = db.relationship('ChiTietGioHang', backref='mon_an', lazy=True)
    chi_tiet_don_hang = db.relationship('ChiTietDonHang', backref='mon_an', lazy=True)

class GioHang(db.Model):
    __tablename__ = 'gioHang'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    nhaHangId = db.Column(db.Integer, db.ForeignKey('nhaHang.id'))
    time = db.Column(db.DateTime, default=datetime.utcnow)

    chi_tiet_gio_hang = db.relationship('ChiTietGioHang', backref='gio_hang', lazy=True)

class ChiTietGioHang(db.Model):
    __tablename__ = 'chiTietGioHang'

    id = db.Column(db.Integer, primary_key=True)
    idMonAn = db.Column(db.Integer, db.ForeignKey('monAn.id'))
    idGioHang = db.Column(db.Integer, db.ForeignKey('gioHang.id'))
    soLuong = db.Column(db.Integer)

class DonHang(db.Model):
    __tablename__ = 'donHang'

    id = db.Column(db.Integer, primary_key=True)
    idKH = db.Column(db.Integer, db.ForeignKey('user.id'))
    idNhaHang = db.Column(db.Integer, db.ForeignKey('nhaHang.id'))
    trangThai = db.Column(db.Enum(EnumStatus), default=EnumStatus.cho)
    thoiGian = db.Column(db.DateTime, default=datetime.utcnow)
    tongGia = db.Column(db.Float)

    chi_tiet_don_hang = db.relationship('ChiTietDonHang', backref='don_hang', lazy=True)

class ChiTietDonHang(db.Model):
    __tablename__ = 'chiTietDonHang'

    id = db.Column(db.Integer, primary_key=True)
    idDH = db.Column(db.Integer, db.ForeignKey('donHang.id'))
    idMonAn = db.Column(db.Integer, db.ForeignKey('monAn.id'))
    soLuong = db.Column(db.Integer)

class DanhGia(db.Model):
    __tablename__ = 'danhGia'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    sao = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        #
        #
        # if DanhMucMonAn.query.count() == 0:
        #     danh_muc_list = [
        #         "Khai vị", "Món chính", "Đồ chay", "Thức uống", "Tráng miệng",
        #         "Bánh kem", "Lẩu", "Đồ nướng", "Đồ ăn nhanh", "Đặc sản địa phương"
        #     ]
        #     for ten in danh_muc_list:
        #         db.session.add(DanhMucMonAn(tenDanhMuc=ten))
        #     db.session.commit()
        #
        # if User.query.count() == 0:
        #     admin = User(
        #         name='admin',
        #         username='admin',
        #         email='admin123@gmail.com',
        #         password=hashlib.md5('123456'.encode('utf-8')).hexdigest(),
        #         role=EnumRole.admin
        #     )
        #
        #     nha_hang = NhaHang(
        #         name='shop1',
        #         username='shop1',
        #         email='staff123@gmail.com',
        #         password=hashlib.md5('123456'.encode('utf-8')).hexdigest(),
        #         role=EnumRole.nhaHang,
        #         adress='123 Nguyễn Văn A, TP.HCM',
        #         MST='0312345678'
        #     )
        #
        #     db.session.add_all([admin, nha_hang])
        #     db.session.commit()
        #
        # if MonAn.query.count() == 0:
        #     nha_hang_staff = NhaHang.query.filter_by(username='shop1').first()
        #
        #     # Lấy các danh mục theo tên
        #     dm_khai_vi = DanhMucMonAn.query.filter_by(tenDanhMuc="Khai vị").first()
        #     dm_mon_chinh = DanhMucMonAn.query.filter_by(tenDanhMuc="Món chính").first()
        #     dm_do_chay = DanhMucMonAn.query.filter_by(tenDanhMuc="Đồ chay").first()
        #     dm_thuc_uong = DanhMucMonAn.query.filter_by(tenDanhMuc="Thức uống").first()
        #     dm_trang_mieng = DanhMucMonAn.query.filter_by(tenDanhMuc="Tráng miệng").first()
        #
        #     mon_an_list = [
        #         {"name": "Gỏi cuốn tôm thịt", "gia": 30000, "dm": dm_khai_vi,
        #          "img": "https://khaihoanphuquoc.com.vn/wp-content/uploads/2023/11/nu%CC%9Bo%CC%9B%CC%81c-ma%CC%86%CC%81m-cha%CC%82%CC%81m-go%CC%89i-cuo%CC%82%CC%81n.png",
        #          "desc": "Gỏi cuốn với tôm, thịt ba chỉ, rau sống và bún, ăn kèm nước chấm đậm đà."},
        #
        #         {"name": "Chả giò rế", "gia": 25000, "dm": dm_khai_vi,
        #          "img": "https://i.ytimg.com/vi/xhsctW9b_oY/maxresdefault.jpg",
        #          "desc": "Chả giò giòn rụm cuốn nhân thịt, mộc nhĩ và miến, chiên vàng hấp dẫn."},
        #
        #         {"name": "Phở bò tái", "gia": 55000, "dm": dm_mon_chinh,
        #          "img": "https://monngonmoingay.com/wp-content/smush-webp/2024/06/pho-tai-lan.jpg.webp",
        #          "desc": "Phở với nước dùng xương bò hầm đậm vị, thịt bò tái mềm và thơm."},
        #
        #         {"name": "Cơm tấm sườn bì", "gia": 50000, "dm": dm_mon_chinh,
        #          "img": "https://cdn.tgdd.vn/2020/08/CookProduct/52-1200x676.jpg",
        #          "desc": "Cơm tấm nóng hổi ăn kèm sườn nướng, bì, trứng và nước mắm pha chua ngọt."},
        #
        #         {"name": "Bún bò Huế", "gia": 55000, "dm": dm_mon_chinh,
        #          "img": "https://hoasenfoods.vn/wp-content/uploads/2024/01/bun-bo-hue.jpg",
        #          "desc": "Đặc sản Huế với sợi bún to, nước dùng cay thơm và giò heo hấp dẫn."},
        #
        #         {"name": "Mì xào giòn hải sản", "gia": 65000, "dm": dm_mon_chinh,
        #          "img": "https://cdn.netspace.edu.vn/images/2021/07/18/cach-lam-mi-xao-hai-san-800.jpg",
        #          "desc": "Mì chiên giòn ăn kèm hải sản, rau củ, sốt sánh đậm đà chuẩn vị nhà hàng."},
        #
        #         {"name": "Đậu hũ chiên sả ớt", "gia": 35000, "dm": dm_do_chay,
        #          "img": "https://file.hstatic.net/1000394081/article/huong-dan-lam-dau-phu-chien-sa-ot-thom-ngon-hap-dan_0c1cca69161e4f56998f5d91d726a869.jpg",
        #          "desc": "Món chay đơn giản mà ngon miệng, đậu hũ chiên vàng cùng sả và ớt thơm."},
        #
        #         {"name": "Cà tím nướng mỡ hành", "gia": 30000, "dm": dm_do_chay,
        #          "img": "https://file.hstatic.net/200000700229/article/lam-ca-tim-nuong-mo-hanh-bang-noi-chien-khong-dau_95456b83f1fa4910a60342e76347b907.jpg",
        #          "desc": "Cà tím nướng mềm béo, rưới mỡ hành thơm lừng, ăn kèm mắm chua ngọt."},
        #
        #         {"name": "Canh chua chay", "gia": 40000, "dm": dm_do_chay,
        #          "img": "https://bientauvannguyenlieu.giadinhnestle.com.vn/sites/default/files/styles/wide/public/recipes-photo/recipe_1691730251.jpg",
        #          "desc": "Canh thanh mát với me, thơm, đậu bắp, đậu hũ và rau ngò om."},
        #
        #         {"name": "Trà đào cam sả", "gia": 25000, "dm": dm_thuc_uong,
        #          "img": "https://www.huongnghiepaau.com/wp-content/uploads/2017/07/tra-dao-cam-sa-ngot-ngao.jpg",
        #          "desc": "Thức uống mát lạnh kết hợp trà, đào, cam và sả, giải khát tuyệt vời."},
        #
        #         {"name": "Trà sữa trân châu đường đen", "gia": 30000, "dm": dm_thuc_uong,
        #          "img": "https://xingfuvietnam.vn/wp-content/uploads/2023/02/xingfu-tra-sua-tran-chau-duong-den-2-FILEminimizer.jpg",
        #          "desc": "Trà sữa béo ngậy kết hợp cùng trân châu dẻo ngọt, đường đen thơm nồng."},
        #
        #         {"name": "Soda chanh dây", "gia": 28000, "dm": dm_thuc_uong,
        #          "img": "https://product.hstatic.net/200000534989/product/soda_chanh_day_b67dce1ee92b4ce78354516caacb54ac.jpg",
        #          "desc": "Soda chua ngọt kết hợp vị chanh dây, giúp tỉnh táo tức thì."},
        #
        #         {"name": "Sinh tố bơ", "gia": 32000, "dm": dm_thuc_uong,
        #          "img": "https://www.cet.edu.vn/wp-content/uploads/2021/05/cach-lam-sinh-to-bo.jpg",
        #          "desc": "Sinh tố bơ đặc sánh, ngậy béo tự nhiên, thêm chút sữa đặc ngon tuyệt."},
        #
        #         {"name": "Bánh flan caramel", "gia": 20000, "dm": dm_trang_mieng,
        #          "img": "https://www.huongnghiepaau.com/wp-content/uploads/2019/04/cach-lam-banh-flan-pho-mai.jpg",
        #          "desc": "Món tráng miệng truyền thống, mềm mịn với lớp caramel ngọt thơm."},
        #
        #         {"name": "Chè khúc bạch", "gia": 30000, "dm": dm_trang_mieng,
        #          "img": "https://cdn.mediamart.vn/images/news/huong-dan-cach-lam-che-khuc-bach-thanh-mat-thom-ngon-hap-dan_ada6ac3c.png",
        #          "desc": "Thạch khúc bạch mềm, mát lạnh, kết hợp với nhãn, hạnh nhân và nước đường."},
        #
        #         {"name": "Kem dừa Thái Lan", "gia": 35000, "dm": dm_trang_mieng,
        #          "img": "https://file.hstatic.net/200000721249/file/cach-lam-kem-trai-dua_thai_lan_57665d316101497e82b36f7fa95dab60.jpg",
        #          "desc": "Kem thơm mát, phục vụ trong trái dừa xiêm kèm topping hấp dẫn."},
        #
        #         {"name": "Bánh crepe sầu riêng", "gia": 40000, "dm": dm_trang_mieng,
        #          "img": "https://web.hn.ss.bfcplatform.vn/newskymarket/product/20242/banh-crepe-sau-rieng-ngan-lop-phu-si-m.jpg",
        #          "desc": "Bánh crepe mỏng cuốn nhân kem lạnh và sầu riêng thơm béo đặc trưng."},
        #
        #         {"name": "Chè bưởi", "gia": 25000, "dm": dm_trang_mieng,
        #          "img": "https://dayphache.edu.vn/wp-content/uploads/2021/05/thanh-pham-che-buoi-dep-mat.jpg",
        #          "desc": "Chè truyền thống nấu từ cùi bưởi giòn dai, đậu xanh và nước cốt dừa."},
        #
        #         {"name": "Cơm rang trứng", "gia": 45000, "dm": dm_mon_chinh,
        #          "img": "https://i-giadinh.vnecdn.net/2023/10/25/Buoc-5-5-1688-1698218565.jpg",
        #          "desc": "Cơm chiên vàng đều cùng trứng, hành lá, nước tương thơm lừng."},
        #
        #         {"name": "Mì cay Hàn Quốc", "gia": 60000, "dm": dm_mon_chinh,
        #          "img": "https://i-dulich.vnecdn.net/2023/12/04/my-cay-jpeg-4190-1701685273.jpg",
        #          "desc": "Mì cay vị Hàn Quốc với hải sản, bò, nấm và nước súp đậm đà cay nồng."}
        #     ]
        #
        #     for mon in mon_an_list:
        #         db.session.add(MonAn(
        #             name=mon['name'],
        #             chiTietMon=mon['desc'],
        #             gia=mon['gia'],
        #             img=mon['img'],
        #             idDanhMuc=mon['dm'].id,
        #             idNhaHang=nha_hang_staff.id
        #         ))
        #
        #     db.session.commit()
        #

        if DanhGia.query.count() == 0:
            khach_hang = User.query.filter_by(username='kh01').first()
            pho_bo = MonAn.query.filter_by(name='Phở bò tái').first()
            tra_sua = MonAn.query.filter_by(name='Trà sữa trân châu đường đen').first()

            dg1 = DanhGia(
                content="Phở rất ngon, nước dùng đậm đà!",
                sao=5,
                user_id=khach_hang.id
            )

            dg2 = DanhGia(
                content="Trà sữa ngon nhưng hơi ngọt với mình.",
                sao=4,
                user_id=khach_hang.id
            )

            db.session.add_all([dg1, dg2])
            db.session.commit()


