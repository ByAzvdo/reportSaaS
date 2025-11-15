from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    fried_item = Column(String(255))
    lot_number = Column(String(100))
    date = Column(Date, nullable=True)
    start_time = Column(String(50))
    end_time = Column(String(50))
    total_fried = Column(Integer)
    goal = Column(Integer)
    oil_lot = Column(String(100))
    comments = Column(Text)
    team = Column(String(255))
    leader_signature = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    cooling_checks = relationship("CoolingCheck", back_populates="report", cascade="all, delete-orphan")

class CoolingCheck(Base):
    __tablename__ = "cooling_checks"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))
    time = Column(String(50))
    temperature = Column(String(50))
    personnel = Column(String(100))
    corrective_action = Column(Text)
    verification_signature = Column(String(255))
    report = relationship("Report", back_populates="cooling_checks")
