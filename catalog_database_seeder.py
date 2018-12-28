#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database_setup import Category, Item, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


categories = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snowboarding',
              'Rock Climbing', 'Football', 'Skating', 'Hockey']

for category in categories:
    session.add(Category(name=category))
    session.commit()

print("all the categories have been added to the database")
