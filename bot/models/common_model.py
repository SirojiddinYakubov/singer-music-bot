from .base_model import BaseModel
import sqlalchemy as db
from sqlalchemy.orm import relationship, validates
from aiogram.utils.i18n import gettext as _


class User(BaseModel):
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    lang_code = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return self.full_name


class Music(BaseModel):
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    created_by = relationship(User, foreign_keys=[created_by_id], backref="musics", lazy="selectin")

    __table_args__ = (db.CheckConstraint(0 < price, name='check_price'), {})

    def __repr__(self):
        return self.title

    @validates('price')
    def validate_price(self, key, value):
        if value <= 0:
            raise Exception(_("Narx 0 dan katta bo'lishi kerak!"))
        return value


class Purchase(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    user = relationship(User, foreign_keys=[user_id], backref="purchases", lazy="selectin")
    music = relationship(Music, foreign_keys=[music_id], backref="purchases", lazy="selectin")
