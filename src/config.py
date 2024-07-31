"""Config file for Oxygen CS. Responsible for creating the database engine and session."""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# dotenv_path = '../.env'
# if not os.path.exists(dotenv_path):
#     raise FileNotFoundError(f"{dotenv_path} does not exist")

# load_dotenv(dotenv_path=dotenv_path)

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url)


SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()

print("LAST PRINT: ", os.getenv("DATABASE_URL"))
