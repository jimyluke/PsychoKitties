import uuid
from dataclasses import dataclass

from flask_sqlalchemy import Model
from sqlalchemy import Column, String, Integer, Float, DateTime, Numeric, text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Collection(Base):
    __tablename__ = 'collections'

    id = Column(String(255), primary_key=True)
    name = Column(String(128), nullable=False)
    owners = Column(Integer)
    total_sales = Column(Float)


class History(Base):
    __tablename__ = 'history'

    def __init__(self, event, collection):
        try:
            date1 = str(event['bought']).split(".")[0]
            date2 = str(event['held_until']).split(".")[0]
            date1 = str(date1).replace("T", " ")
            date2 = str(date2).replace("T", " ")
        except TypeError:
            print("xxxxxxxxxxxxx")
            print(event)
        self.username = event['username']
        self.twitter = event['twitter']
        self.editionId = event['editionId']
        self.croWalletAddress = event['croWallet']
        self.bought_on = date1
        self.held_until = date2
        self.id = event['id']
        try:
            self.price = event['price']
        except:
            self.price = 0
        self.nature = event['txType']
        self.collection = collection

    username = Column(String(64))
    twitterUsername = Column(String(64))
    croWalletAddress = Column(String(128), nullable=False)
    id = Column(String(128), primary_key=True)
    bought_on = Column(DateTime, nullable=False)
    held_until = Column(DateTime, nullable=False)
    nature = Column(String(128), nullable=False)
    price = Column(Numeric(10, 3), nullable=False)
    collection = Column(String(128))
    editionId = Column(String(128), nullable=False)


@dataclass
class Kitty(Base):
    rank: int
    Score: float
    Background: str
    Body: str
    Clothes: str
    Mouth: str
    Nose: str
    Eyes: str
    Hat: str
    collection: str
    assetId: str
    name: str
    defaultEditionId: str
    copies: str
    description: str
    creator_avatar: str
    main_url: str
    cover_url: str

    __tablename__ = 'kitties'

    ID = Column(Integer, primary_key=True)
    rank = Column(Integer)
    Score = Column(Numeric(11, 7), nullable=False)
    Background = Column(String(27))
    Body = Column(String(27))
    Clothes = Column(String(27))
    Mouth = Column(String(27))
    Nose = Column(String(27))
    Eyes = Column(String(27))
    Hat = Column(String(27))
    collection = Column(String(255), server_default=text("'kitty'"))
    assetId = Column(String(255))
    name = Column(String(255))
    defaultEditionId = Column(String(255))
    copies = Column(String(255))
    description = Column(String(255))
    creator_avatar = Column(String(255))
    main_url = Column(String(255))
    cover_url = Column(String(255))


@dataclass
class User(Base):
    """Data model for user accounts."""
    id: int
    username: str
    isHolder: bool
    isTwitterMatching: bool
    discordUsername: str
    cryptoUsername: str
    cryptoNumber: int

    __tablename__ = 'psychokitties_users'
    id = Column(String(100), default=uuid.uuid4.__str__())
    username = Column(
        String(64), primary_key=True
    )
    cryptoUsername = Column(
        String(64)
    )
    discordUsername = Column(
        String(64)
    )
    isTwitterMatching = Column(
        Boolean
    )
    isHolder = Column(
        Boolean
    )
    discordId = Column(
        Integer
    )
    cryptoNumber = Column(
        Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)
