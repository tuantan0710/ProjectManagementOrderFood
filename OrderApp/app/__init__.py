from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'JKDFKDFNEI4**7tyB^^b9HNJDFICB2@@@'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/fooddb?charset=utf8mb4" % quote('Tuan@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(
    cloud_name="dqtk7akkz",
    api_key="175943162423538",
    api_secret="yUVCdUHmqdgTU5OMH68op0ADdsc",
    secure=True
)