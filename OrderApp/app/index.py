from flask import render_template, request, redirect, url_for, session, abort, jsonify, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from app import dao, app, login, db, utils, socketio
from app.models import DanhMucMonAn, MonAn, NhaHang, EnumRole, DonHang, ChiTietDonHang, EnumStatus, DanhGia, ThongBao
import cloudinary.uploader

from app.utils import send_gmail

from flask import render_template, make_response
from xhtml2pdf import pisa
import io, os

from flask_socketio import join_room

@socketio.on('join')
def handle_join(data):
    room = data.get("room")
    if room:
        join_room(room)
        print(f"Client joined room: {room}")

@app.route('/xuat-bill/<int:id>')
def xuat_bill(id):
    don_hang = DonHang.query.get_or_404(id)

    html = render_template('restaurent/bill_template.html', dh=don_hang)

    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_buffer)

    if pisa_status.err:
        return f"Lỗi khi tạo PDF: {pisa_status.err}", 500

    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=hoadon_{don_hang.id}.pdf'
    return response
@app.route('/')
def index():
    kw = request.args.get('kw', '')
    cates = dao.load_categories()
    foods = dao.load_foods(keyword=kw)
    return render_template('index.html', categories=cates, foods=foods, kw=kw)
@app.route('/nha-hang', methods=['GET'])
def danh_sach_nha_hang():
    kw = request.args.get('kw', '')
    nha_hangs = dao.load_nha_hang(keyword=kw)  # hàm đã có sẵn
    return render_template('nha_hang_list.html', nha_hangs=nha_hangs, kw=kw)

@app.route('/danh-muc/<int:category_id>')
def food_by_category(category_id):
    categories = DanhMucMonAn.query.all()
    foods = MonAn.query.filter_by(idDanhMuc=category_id).all()
    return render_template('index.html', categories=categories, foods=foods)

@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            next = request.args.get('next')
            return redirect(next if next else '/')

    return render_template('login.html')
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')

@app.route("/register", methods=['get', 'post'])
def register_process():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password == confirm:
            email = request.form.get('email')
            if not email:
                err_msg = 'Email là bắt buộc!'
            else:
                data = request.form.copy()
                del data['confirm']

                avt = request.files.get('avt')
                dao.add_user(avt=avt, **data)
                return redirect('/login')
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)

@app.route("/nha-hang/<int:nha_hang_id>")
def chi_tiet_nha_hang(nha_hang_id):
    nha_hang = NhaHang.query.get_or_404(nha_hang_id)
    danh_sach_mon = MonAn.query.filter_by(idNhaHang=nha_hang.id).all()

    return render_template("restaurentDetail.html", nha_hang=nha_hang, foods=danh_sach_mon)

@app.route('/api/cap-nhat-mon/<int:mon_an_id>', methods=['POST'])
@login_required
def api_cap_nhat_mon(mon_an_id):
    data = request.get_json()
    tinh_trang_moi_raw = data.get('tinh_trang_moi')


    tinh_trang_moi = tinh_trang_moi_raw in ['true', 'True', True, 1, '1']

    mon = db.session.get(MonAn, mon_an_id)
    if not mon:
        return jsonify({'status': 'error', 'message': 'Món không tồn tại'}), 404


    if mon.nha_hang.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Không có quyền'}), 403


    mon.tinhTrang = tinh_trang_moi
    db.session.commit()

    return jsonify({'status': 'success', 'tinh_trang': mon.tinhTrang})

@app.route('/mon-an/<int:food_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_food(food_id):
    mon = MonAn.query.get_or_404(food_id)

    if current_user.role != EnumRole.nhaHang or mon.idNhaHang != current_user.id:
        abort(403)

    if request.method == 'POST':
        mon.name = request.form['name']
        mon.gia = request.form['gia']
        mon.chiTietMon = request.form['chiTietMon']
        mon.tinhTrang = request.form.get('tinhTrang') == 'on'

        img_file = request.files.get('img')
        if img_file and img_file.filename != '':
            # Upload lên Cloudinary
            res = cloudinary.uploader.upload(img_file)
            mon.img = res['secure_url']

        db.session.commit()
        return redirect(url_for('chi_tiet_nha_hang', nha_hang_id=current_user.id))

    return render_template('restaurent/edit_food.html', food=mon)

from collections import defaultdict

@app.route("/nha-hang/don-hang")
@login_required
def quan_ly_don_hang():
    if current_user.role != EnumRole.nhaHang:
        return "Bạn không có quyền truy cập", 403

    trang_thai = request.args.get("trang_thai")
    sap_xep = request.args.get("sap_xep", "desc")
    ma_don = request.args.get("ma_don", type=int)

    query = DonHang.query.filter(DonHang.idNhaHang == current_user.id)

    if ma_don:
        query = query.filter(DonHang.id == ma_don)

    if trang_thai:
        try:
            query = query.filter(DonHang.trangThai == EnumStatus[trang_thai])
        except KeyError:
            pass

    if sap_xep == "asc":
        query = query.order_by(DonHang.thoiGian.asc())
    else:
        query = query.order_by(DonHang.thoiGian.desc())

    don_hang = query.all()

    # Tổng hợp món từ các đơn "chờ"
    mon_dang_cho = defaultdict(int)
    don_cho = DonHang.query.filter(
        DonHang.idNhaHang == current_user.id,
        DonHang.trangThai == EnumStatus.cho
    ).all()

    for dh in don_cho:
        for ct in dh.chi_tiet_don_hang:
            mon_dang_cho[ct.mon_an.name] += ct.soLuong

    return render_template(
        "restaurent/quan_ly_don_hang.html",
        don_hang=don_hang,
        trang_thai_hien_tai=trang_thai,
        sap_xep_hien_tai=sap_xep,
        ma_don_hien_tai=ma_don,
        tong_mon_dang_cho=mon_dang_cho
    )

@app.route('/chi-tiet-don-hang-modal/<int:id>')
def chi_tiet_don_hang_modal(id):
    don_hang = DonHang.query.get_or_404(id)
    return render_template('restaurent/chi_tiet_modal.html', don_hang=don_hang)
@app.post('/don-hang/<int:id>/xac-nhan')
@login_required
def xac_nhan_don(id):
    don = DonHang.query.get_or_404(id)
    if don.trangThai.name == 'cho':
        don.trangThai = EnumStatus.daXacNhan
        db.session.commit()
    return redirect(url_for('quan_ly_don_hang'))


@app.post('/don-hang/<int:id>/giao')
@login_required
def giao_don(id):
    don = DonHang.query.get_or_404(id)
    if don.trangThai.name == 'daXacNhan':
        don.trangThai = EnumStatus.daGiao
        db.session.commit()
    return redirect(url_for('quan_ly_don_hang'))


@app.route('/don-hang/<int:id>/huy', methods=['POST'])
def huy_don(id):
    ly_do = request.form.get('ly_do_huy')
    don_hang = DonHang.query.get_or_404(id)
    don_hang.trangThai = EnumStatus.DA_HUY
    don_hang.ly_do_huy = ly_do
    db.session.commit()
    flash('Đã hủy đơn hàng.', 'success')
    return redirect(url_for('danh_sach_don_hang'))
@app.route('/nha-hang/don-hang/<int:id>', methods=['GET', 'POST'])
@login_required
def chi_tiet_don_hang(id):
    if current_user.role != EnumRole.nhaHang:
        return "Bạn không có quyền truy cập", 403

    don_hang = DonHang.query.get_or_404(id)
    if don_hang.idNhaHang != current_user.id:
        return "Không có quyền xem đơn hàng này", 403

    chi_tiet = ChiTietDonHang.query.filter_by(idDH=id).all()

    if request.method == 'POST':
        new_status = request.form.get('trangThai')
        note = request.form.get('noiDungHuy', '').strip()

        # Kiểm tra nếu hủy mà không nhập lý do
        if new_status == 'daHuy' and not note:
            flash("Phải nhập lý do khi hủy đơn hàng!", "danger")
        else:
            try:
                don_hang.trangThai = EnumStatus[new_status]
                db.session.commit()

                # Gửi email
                subject = f"Đơn hàng #{don_hang.id} - Trạng thái mới: {don_hang.trangThai.value}"
                content = f"""
                    <p>Xin chào {don_hang.khach_hang.name},</p>
                    <p>Đơn hàng của bạn đã được cập nhật trạng thái: <strong>{don_hang.trangThai.value}</strong></p>
                """

                if new_status == 'daHuy' and note:
                    content += f"<p><strong>Lý do hủy:</strong> {note}</p>"

                send_gmail(don_hang.khach_hang.email, subject, content)
                flash("Cập nhật và gửi email thành công!", "success")

            except Exception as e:
                print("Lỗi cập nhật trạng thái:", e)
                flash("Có lỗi xảy ra khi cập nhật đơn hàng!", "danger")

            return redirect(url_for('chi_tiet_don_hang', id=id))

    return render_template('restaurent/chi_tiet_don_hang.html', don_hang=don_hang, chi_tiet=chi_tiet)

@app.route('/register-nhahang', methods=['get', 'post'])
def register_nhahang():
    err_msg = None
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password == confirm:
            data = request.form.copy()
            del data['confirm']
            avt = request.files.get('avt')

            try:
                dao.add_nha_hang(avt=avt, **data)
                return redirect('/login')
            except Exception as e:
                err_msg = f"Lỗi: {str(e)}"
        else:
            err_msg = "Mật khẩu không khớp!"

    return render_template('register_nhahang.html', err_msg=err_msg)



from flask_socketio import emit

@app.route('/mon-an/<int:id>', methods=['GET', 'POST'])
def chi_tiet_mon_an(id):
    mon_an = MonAn.query.get_or_404(id)

    if request.method == 'POST':
        if not current_user.is_authenticated or current_user.role != EnumRole.khachHang:
            flash("Bạn cần đăng nhập bằng tài khoản khách hàng để đánh giá.", "warning")
            return redirect(url_for('login'))

        sao = int(request.form.get('sao'))
        content = request.form.get('content')

        danh_gia = DanhGia(
            content=content,
            sao=sao,
            user_id=current_user.id,
            mon_an_id=mon_an.id
        )
        db.session.add(danh_gia)
        db.session.commit()

        nha_hang_id = mon_an.idNhaHang
        noi_dung_tb = f"{current_user.name} đã đánh giá món: {mon_an.name} ⭐ {sao}/5"
        url = url_for('chi_tiet_mon_an', id=mon_an.id)

        thong_bao = ThongBao(
            noi_dung=noi_dung_tb,
            user_id=nha_hang_id,
            url=url
        )
        db.session.add(thong_bao)
        db.session.commit()

        socketio.emit(
            "thong_bao_moi",
            {"noi_dung": noi_dung_tb,
             "url": url
             },
            room=f"user_{nha_hang_id}"
        )

        flash("Đánh giá đã được gửi!", "success")
        return redirect(url_for('chi_tiet_mon_an', id=mon_an.id))

    return render_template('monAnDetail.html', mon_an=mon_an)



@app.route("/mon-an/add", methods=['GET', 'POST'])
@login_required
def them_mon_an():
    if current_user.role != EnumRole.nhaHang:
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name')
        gia = request.form.get('gia')
        chi_tiet = request.form.get('chiTietMon')
        id_danh_muc = request.form.get('idDanhMuc')
        img = request.files.get('img')

        img_url = None
        if img:
            upload = cloudinary.uploader.upload(img)
            img_url = upload.get('secure_url')

        mon = MonAn(
            name=name,
            gia=float(gia),
            chiTietMon=chi_tiet,
            idDanhMuc=int(id_danh_muc),
            idNhaHang=current_user.id,
            img=img_url
        )
        db.session.add(mon)
        db.session.commit()

        return redirect(f"/nha-hang/{current_user.id}")

    danh_mucs = DanhMucMonAn.query.all()
    return render_template("restaurent/them_mon_an.html", danh_mucs=danh_mucs)


from flask import request
from datetime import datetime
from sqlalchemy import extract
import calendar

@app.route("/nha-hang/thong-ke-doanh-thu")
@login_required
def thong_ke_doanh_thu():
    if current_user.role != EnumRole.nhaHang:
        return "Không có quyền truy cập", 403


    thang = request.args.get('thang', type=int) or datetime.now().month
    nam = request.args.get('nam', type=int) or datetime.now().year


    don_hang = DonHang.query.filter(
        DonHang.idNhaHang == current_user.id,
        DonHang.trangThai == EnumStatus.daGiao,
        extract('month', DonHang.thoiGian) == thang,
        extract('year', DonHang.thoiGian) == nam
    ).all()


    tong_doanh_thu = sum(dh.tongGia for dh in don_hang)


    so_ngay = calendar.monthrange(nam, thang)[1]
    doanh_thu_ngay = [0] * so_ngay

    for dh in don_hang:
        ngay = dh.thoiGian.day
        doanh_thu_ngay[ngay - 1] += dh.tongGia

    return render_template("restaurent/thong_ke.html",
                           don_hang=don_hang,
                           tong_doanh_thu=tong_doanh_thu,
                           doanh_thu_ngay=doanh_thu_ngay,
                           thang=thang, nam=nam)
@app.route("/nha-hang/cap-nhat-thong-tin", methods=["GET", "POST"])
@login_required
def cap_nhat_nha_hang():
    if current_user.role != EnumRole.nhaHang:
        return "Không có quyền truy cập", 403

    nha_hang = NhaHang.query.get(current_user.id)

    if request.method == "POST":
        # Cập nhật thông tin cơ bản
        nha_hang.name = request.form["name"]
        nha_hang.email = request.form["email"]
        nha_hang.phone = request.form["phone"]
        nha_hang.adress = request.form["adress"]
        nha_hang.MST = request.form["MST"]
        nha_hang.gio_mo_cua = request.form["gio_mo_cua"]
        nha_hang.gio_dong_cua = request.form["gio_dong_cua"]

        # Cập nhật ảnh đại diện nếu có
        file = request.files.get('avt')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            nha_hang.avt = url_for('static', filename=f'uploads/{filename}')

        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        return redirect(url_for("chi_tiet_nha_hang", nha_hang_id=nha_hang.id))

    return render_template("restaurent/nha_hang_cap_nhat.html", nha_hang=nha_hang)

@app.context_processor
def inject_thong_bao():
    thong_bao = []
    chua_doc = 0
    if current_user.is_authenticated:
        thong_bao = ThongBao.query.filter_by(user_id=current_user.id).order_by(ThongBao.thoi_gian.desc()).all()
        chua_doc = ThongBao.query.filter_by(user_id=current_user.id, da_doc=False).count()

    return dict(ds_thong_bao=thong_bao, so_thong_bao=chua_doc)

@app.route("/api/nha-hang/<int:nha_hang_id>/doi-trang-thai", methods=["POST"])
@login_required
def doi_trang_thai_hoat_dong(nha_hang_id):
    nha_hang = NhaHang.query.get_or_404(nha_hang_id)

    if current_user.id != nha_hang.id:
        return {"error": "Không có quyền thực hiện"}, 403

    nha_hang.dang_hoat_dong = not nha_hang.dang_hoat_dong
    db.session.commit()

    return {"dang_hoat_dong": nha_hang.dang_hoat_dong}

@app.route('/api/thong-bao/<int:id>/danh-dau-da-doc', methods=['POST'])
@login_required
def danh_dau_thong_bao(id):
    from app.models import ThongBao
    from app import db

    tb = ThongBao.query.get(id)
    if not tb or tb.user_id != current_user.id:
        return jsonify({'success': False}), 403

    tb.da_doc = True
    db.session.commit()

    return jsonify({'success': True})

@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == '__main__':
    socketio.run(app, debug=True)