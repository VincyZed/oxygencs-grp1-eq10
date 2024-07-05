"""Config file for Oxygen CS. Responsible for creating the database engine and session."""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgresql://user01eq10:DQKDYh4ISzVTvgI8@157.230.69.113:5432/db01eq10")

SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()
