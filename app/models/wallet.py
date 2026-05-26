from sqlalchemy import Column, String, Integer

from app.db import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    uuid = Column(String(36), primary_key=True)
    balance = Column(Integer)
