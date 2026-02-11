import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

db = sa.create_engine('sqlite:///:memory:') # todo: replace connection
Session = sessionmaker(bind=db) 

