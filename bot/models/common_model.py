from .base_model import BaseModel
import sqlalchemy as db


class User(BaseModel):
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    lang_code = db.Column(db.String(5), nullable=False)

# class Singer(BaseModel):
#     first_name = db.Column(db.String(100), nullable=False)
#     last_name = db.Column(db.String(100), nullable=True)


class Music(BaseModel):
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
