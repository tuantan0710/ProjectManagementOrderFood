from flask_socketio import SocketIO
from urllib.parse import quote

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
import cloudinary
from app.custom_admin import MyAdminIndexView

app = Flask(__name__)
app.secret_key = 'JKDFKDFNEI4**7tyB^^b9HNJDFICB2@@@'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/fooddb?charset=utf8mb4" % quote('Admin@123')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
db = SQLAlchemy(app)
login = LoginManager(app)

admin = Admin(app,
    name='Trang chủ quản trị',     # Tên hiển thị trên header
    index_view=MyAdminIndexView(name='Trang chủ'),  # ← Đây là tên của "Home"
    template_mode='bootstrap4')
app.secret_key='iaur98rq945o7qu0r^%*hUI9*3i'


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Thay bằng server bạn dùng
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nguyentrunganhtuan201004@gmail.com'  # Email của bạn
app.config['MAIL_PASSWORD'] = 'lzbj zbuv fgmy uqae' # Mật khẩu ứng dụng hoặc API key
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)
cloudinary.config(
    cloud_name="dqtk7akkz",
    api_key="175943162423538",
    api_secret="yUVCdUHmqdgTU5OMH68op0ADdsc",
    secure=True
)