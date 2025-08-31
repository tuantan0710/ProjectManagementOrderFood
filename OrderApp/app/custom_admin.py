from flask_admin import AdminIndexView, expose
from flask_login import current_user
from flask import redirect, url_for, render_template

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login_process'))  # Hoặc route login của bạn
        # Truyền biến vào template nếu muốn hiển thị thông tin người dùng
        return self.render('admin/custom_index.html', user=current_user)
