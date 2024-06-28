from sqlalchemy import Table, Column, Integer, Numeric, String, DateTime

from config import Base

class Snapshot(Base):
    __tablename__ = "temperatures"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    temperature = Column(Numeric)
    action = Column(String)