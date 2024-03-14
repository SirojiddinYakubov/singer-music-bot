from .base_model import BaseModel
import sqlalchemy as db


class User(BaseModel):
    telegram_id = db.Column(db.Integer, primary_key=True)