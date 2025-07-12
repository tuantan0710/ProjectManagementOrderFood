from flask import render_template

from app import dao, app
from app.models import DanhMucMonAn, MonAn


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

if __name__ == '__main__':
    app.run(debug=True)