from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)


class ElderlyProfile(Base):
    __tablename__ = "elderly_profiles"

    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    medical_notes = Column(Text, nullable=True)
    blood_type = Column(String(5), nullable=True)
    insurance_info = Column(Text, nullable=True)
    isapre_info = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=True)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)


class HealthWorker(Base):
    __tablename__ = "health_workers"

    id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profession = Column(String(100), nullable=True)
    license_number = Column(String(100), nullable=True)
    verification_status = Column(String, default="pending", nullable=True)
    rating = Column(Numeric(3, 2), default=5.00, nullable=True)
    total_appointments = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=True)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduled_datetime = Column(DateTime, nullable=False)
    doctor_name = Column(String(255), nullable=True)
    specialty = Column(String(100), nullable=True)
    address = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="scheduled", nullable=False)
    doctors_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    
    # Foreign keys
    elderly_id = Column(Integer, ForeignKey("elderly_profiles.id", ondelete="CASCADE"), nullable=False)
    health_worker_id = Column(Integer, ForeignKey("health_workers.id", ondelete="CASCADE"), nullable=False)

