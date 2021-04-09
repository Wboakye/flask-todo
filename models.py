import datetime as dt
import json

from flask_login import UserMixin

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    first_name = Column(db.String(80), nullable=False)
    last_name = Column(db.String(80), nullable=False)
    username = Column(db.String(80), unique=True, nullable=False)
    password = Column(db.String(80), nullable=False)
    todos = relationship("ToDo")
    todo_order = Column(db.String(1000), nullable=False, default=json.dumps([]))


class ToDo(db.Model):
    id = Column(Integer, primary_key=True)
    task = Column(db.String(280), nullable=False)
    completed = Column(db.Boolean, nullable=False, default=False)
    created_date = Column(db.DateTime, default=dt.datetime.utcnow)
    due_date = Column(
        db.DateTime,
        nullable=False,
        default=dt.datetime.today(),
    )
    user_id = Column(Integer, ForeignKey("user.id"))
