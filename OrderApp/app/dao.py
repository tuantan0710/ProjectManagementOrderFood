from app.models import DanhMucMonAn, MonAn
def load_categories():
    return DanhMucMonAn.query.all()

def load_foods():
    return MonAn.query.all()