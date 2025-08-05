from flask_admin.contrib.sqla import ModelView
from wtforms.fields import SelectField, PasswordField
from app import admin, db
from app.models import User, NhaHang, MonAn, DonHang, DanhGia, EnumRole,DanhMucMonAn
import hashlib
from flask_admin import expose, AdminIndexView,BaseView
from flask import render_template
from flask_login import login_required
from sqlalchemy import func, extract, case
from app.models import *
from flask import request

class UserModelView(ModelView):
    column_labels = {
        'username': 'Tên đăng nhập',
        'password': 'Mật khẩu',
        'role': 'Vai trò',
        'email': 'Email',
        'created_at': 'Ngày tạo',
    }

    form_overrides = dict(
        role=SelectField,
        password=PasswordField
    )

    form_args = dict(
        role=dict(
            choices=[(e.value, e.name) for e in EnumRole],
            label='Vai trò'
        ),
        username=dict(label='Tên đăng nhập'),
        password=dict(label='Mật khẩu'),
        email=dict(label='Email'),
    )

    column_searchable_list = ['username', 'email']
    column_filters = ['role']
    column_exclude_list = ['password', 'avt']  # Cột không hiển thị
    can_view_details = True

# ModelView cho NhaHang
class NhaHangModelView(ModelView):
    column_labels = {
        'name': 'Tên nhà hàng',
        'adress': 'Địa chỉ',
        'MST': 'Mã số thuế',
        'gio_mo_cua': 'Giờ mở cửa',
        'gio_dong_cua': 'Giờ đóng cửa',
        'dang_hoat_dong': 'Trạng thái hoạt động',
    }

    form_args = dict(
        name=dict(label='Tên nhà hàng'),
        adress=dict(label='Địa chỉ'),
        MST=dict(label='Mã số thuế'),
        gio_mo_cua=dict(label='Giờ mở cửa'),
        gio_dong_cua=dict(label='Giờ đóng cửa'),
        dang_hoat_dong=dict(label='Trạng thái hoạt động'),
    )

    column_exclude_list = ['password', 'avt', 'phone']  # Cột không hiển thị
    column_searchable_list = ['name', 'adress']
    column_filters = ['dang_hoat_dong']
    can_view_details = True

# ModelView cho MonAn
class MonAnModelView(ModelView):
    column_labels = {
        'name': 'Tên món ăn',
        'chiTietMon': 'Chi tiết món',
        'gia': 'Giá',
        'img': 'Hình ảnh',
        'tinhTrang': 'Tình trạng',
        'idDanhMuc': 'Danh mục',
        'idNhaHang': 'Nhà hàng',
    }
    column_exclude_list = ['img']  # Cột không hiển thị

    form_args = dict(
        name=dict(label='Tên món ăn'),
        chiTietMon=dict(label='Chi tiết món'),
        gia=dict(label='Giá'),
        img=dict(label='Hình ảnh'),
        tinhTrang=dict(label='Tình trạng'),
        idDanhMuc=dict(label='Danh mục'),
        idNhaHang=dict(label='Nhà hàng'),
    )

    column_searchable_list = ['name', 'gia']
    column_filters = ['tinhTrang']
    can_view_details = True

    # Không cấp quyền thêm, sửa, xóa
    can_create = False
    can_edit = False
    can_delete = False

# ModelView cho DonHang
class DonHangModelView(ModelView):
    column_labels = {
        'idKH': 'Khách hàng',
        'idNhaHang': 'Nhà hàng',
        'trangThai': 'Trạng thái',
        'thoiGian': 'Thời gian',
        'tongGia': 'Tổng giá',
    }

    form_args = dict(
        idKH=dict(label='Khách hàng'),
        idNhaHang=dict(label='Nhà hàng'),
        trangThai=dict(label='Trạng thái'),
        thoiGian=dict(label='Thời gian'),
        tongGia=dict(label='Tổng giá'),
    )

    column_searchable_list = ['idKH', 'idNhaHang']
    column_filters = ['trangThai']
    can_view_details = True

    # Không cấp quyền thêm, sửa, xóa
    can_create = False
    can_edit = False
    can_delete = False

# ModelView cho DanhGia
class DanhGiaModelView(ModelView):
    column_labels = {
        'content': 'Nội dung',
        'date': 'Ngày',
        'sao': 'Sao',
        'user_id': 'Người dùng',
        'mon_an_id': 'Món ăn',
    }

    form_args = dict(
        content=dict(label='Nội dung'),
        date=dict(label='Ngày'),
        sao=dict(label='Sao'),
        user_id=dict(label='Người dùng'),
        mon_an_id=dict(label='Món ăn'),
    )

    column_searchable_list = ['content', 'sao']
    column_filters = ['user_id', 'mon_an_id']
    can_view_details = True

    # Không cấp quyền thêm, sửa, xóa
    can_create = False
    can_edit = False
    can_delete = False


class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        # 1. Tỉ lệ vai trò tài khoản (khách hàng / nhà hàng / admin)
        role_counts = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
        user_role_data = {
            "labels": [r[0].value for r in role_counts],
            "data": [r[1] for r in role_counts]
        }

        # 2. Nhà hàng đang hoạt động / không hoạt động
        active_counts = db.session.query(
            func.sum(case((NhaHang.dang_hoat_dong == True, 1), else_=0)),
            func.sum(case((NhaHang.dang_hoat_dong == False, 1), else_=0))
        ).first()
        user_active_data = [active_counts[0] or 0, active_counts[1] or 0]

        # 3. Top 5 món ăn bán chạy
        top_foods = db.session.query(
            MonAn.name,
            func.sum(ChiTietDonHang.soLuong)
        ).join(ChiTietDonHang).group_by(MonAn.id).order_by(func.sum(ChiTietDonHang.soLuong).desc()).limit(5).all()
        top_foods_data = {
            "labels": [f[0] for f in top_foods],
            "data": [int(f[1]) for f in top_foods]
        }

        # 4. Trung bình sao cao nhất theo món ăn
        rating_avg = db.session.query(
            MonAn.name,
            func.avg(DanhGia.sao)
        ).join(DanhGia).group_by(MonAn.id).order_by(func.avg(DanhGia.sao).desc()).limit(5).all()
        rating_avg_data = {
            "labels": [r[0] for r in rating_avg],
            "data": [round(r[1], 1) for r in rating_avg]
        }

        # 5. Doanh thu cao nhất theo nhà hàng
        revenue = db.session.query(
            NhaHang.name,
            func.sum(DonHang.tongGia)
        ).join(DonHang).group_by(NhaHang.id).order_by(func.sum(DonHang.tongGia).desc()).limit(5).all()
        revenue_data = {
            "labels": [r[0] for r in revenue],
            "data": [float(r[1]) for r in revenue]
        }

        return self.render('admin/thong_ke.html',
                           user_role_data=user_role_data,
                           user_active_data=user_active_data,
                           top_foods=top_foods_data,
                           rating_avg=rating_avg_data,
                           revenue=revenue_data)

# Thêm các view vào trang admin
admin.add_view(UserModelView(User, db.session,name='Tài Khoản'))
admin.add_view(NhaHangModelView(NhaHang, db.session,name='Tài Khoản Nhà Hàng'))
admin.add_view(MonAnModelView(MonAn, db.session,name='Danh Sách Món Ăn'))
admin.add_view(DonHangModelView(DonHang, db.session,name='Danh Sách Đơn Hàng'))
admin.add_view(DanhGiaModelView(DanhGia, db.session,name='Đánh Giá '))
admin.add_view(ThongKeView(name='Thống kê', endpoint='thong-ke'))
