from flask import Flask
from sqlalchemy.sql.schema import MetaData
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_apscheduler import APScheduler

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

#initialize APscheduler
scheduler = APScheduler()

metadata = MetaData(naming_convention=convention)

app = Flask(__name__)
app.config.from_object(Config)

# this is the same as APScheduler(app) or Admin(app) but leave it so
scheduler.init_app(app)
# starts the scheduler
scheduler.start()

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
admin = Admin(app)
login = LoginManager(app)
login.login_view = 'index'



from app import routes, models, errors, admin_view
