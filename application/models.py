import uuid
from dataclasses import dataclass

from . import db


@dataclass
class User(db.Model):
    """Data model for user accounts."""
    id: int
    username: str
    isHolder: bool
    isTwitterMatching: bool
    discordUsername: str

    __tablename__ = 'psychokitties_users'
    id = db.Column(db.String(100), default=uuid.uuid4.__str__())
    username = db.Column(
        db.String(64), primary_key=True
    )
    cryptoUsername = db.Column(
        db.String(64)
    )
    discordUsername = db.Column(
        db.String(64)
    )
    isTwitterMatching = db.Column(
        db.Boolean
    )
    isHolder = db.Column(
        db.Boolean
    )
    discordId = db.Column(
        db.Integer
    )
    cryptoNumber = db.Column(
        db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)
