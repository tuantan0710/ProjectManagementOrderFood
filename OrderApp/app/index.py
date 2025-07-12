from flask import render_template, request, redirect
from flask_login import login_user, logout_user

from app import dao, app, login
from app.models import DanhMucMonAn, MonAn
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

            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)
            return redirect('/login')
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)

@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)



if __name__ == '__main__':
    app.run(debug=True)