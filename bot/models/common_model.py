from .base_model import BaseModel
import sqlalchemy as db


class User(BaseModel):
    telegram_id = db.Column(db.Integer, primary_key=True)


# class Singer(BaseModel):
#     first_name = db.Column(db.String(100), nullable=False)
#     last_name = db.Column(db.String(100), nullable=True)


class Music(BaseModel):
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)