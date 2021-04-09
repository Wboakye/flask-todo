from auth import auth as auth_blueprint
from main import main as main_blueprint
from models import db, User
from filters import friendly_date

from flask import Flask
from flask_login import LoginManager


# Flask
app = Flask(__name__)
app.config[
    "SECRET_KEY"
] = "\x14B~^\x07\xe1\x197\xda\x18\xa6[[\x05\x03QVg\xce%\xb2<\x80\xa4\x00"
app.config["DEBUG"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
db.init_app(app)


# Auth
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)

# Register template filters
app.jinja_env.filters["friendly_date"] = friendly_date

db.create_all()


if __name__ == "__main__":
    app.run(port=3000)
