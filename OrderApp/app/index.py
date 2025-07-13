from flask import render_template, request, redirect, url_for, session, abort
from flask_login import login_user, logout_user, current_user, login_required

from app import dao, app, login, db
from app.models import DanhMucMonAn, MonAn, NhaHang, EnumRole
import cloudinary.uploader


@app.route('/')
def index():
    cates = dao.load_categories()
    foods = dao.load_foods()
    return render_template('index.html', categories=cates, foods=foods)

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

        if password.__eq__(confirm):
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

@app.route('/mon-an/<int:mon_an_id>/cap-nhat-tinh-trang', methods=['POST'])
@login_required
def cap_nhat_tinh_trang_mon(mon_an_id):
    mon = MonAn.query.get_or_404(mon_an_id)

    if mon.nha_hang.id != current_user.id:
        return redirect(url_for('index'))

    tinh_trang_moi = request.form.get('tinh_trang_moi') == 'True'
    mon.tinhTrang = tinh_trang_moi

    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/mon-an/<int:food_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_food(food_id):
    mon = MonAn.query.get_or_404(food_id)

    # Kiểm tra quyền truy cập
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

    return render_template('edit_food.html', food=mon)



@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == '__main__':
    app.run(debug=True)