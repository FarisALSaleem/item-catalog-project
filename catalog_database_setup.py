#!/usr/bin/env python3

# Configuration
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# End Configuration


# Class
class Category(Base):
    # table information
    __tablename__ = 'category'
    # table mapping
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class User(Base):
    # table information
    __tablename__ = 'user'
    # table mapping
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    picture = Column(String(255), nullable=False)


class Item(Base):
    # table information
    __tablename__ = 'item'
    # table mapping
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'cat_id': self.cat_id,
            'description': self.description,
            'id': self.id,
            'title': self.title
        }


# End class
# insert at end of file
engine = create_engine('postgresql://grader:supersecretpassword@localhost/grader')

Base.metadata.create_all(engine)
