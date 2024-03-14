import datetime
import re
import sqlalchemy as db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base


def camel_to_snake_case(name: str) -> str:
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', name).lower()

class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake_case(cls.__name__)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column('created_at', db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column('updated_at', db.DateTime, onupdate=datetime.datetime.utcnow)


# Base = declarative_base()
BaseModel = declarative_base(cls=BaseModel)