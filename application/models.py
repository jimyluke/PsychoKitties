import uuid

from . import db


class User(db.Model):
    """Data model for user accounts."""

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

    def __repr__(self):
        return '<User {}>'.format(self.username)
