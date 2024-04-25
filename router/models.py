from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Table(Base):
    __tablename__ = "mytable"
    uuid = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(String)
    link = Column(String)
    quantity = Column(String)
