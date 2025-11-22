from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppointmentCreate(BaseModel):
    scheduled_datetime: datetime
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    address: str
    description: Optional[str] = None
    status: str = "scheduled"
    doctors_notes: Optional[str] = None
    elderly_id: int
    health_worker_id: int


class AppointmentUpdate(BaseModel):
    scheduled_datetime: Optional[datetime] = None
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    doctors_notes: Optional[str] = None
    elderly_id: Optional[int] = None
    health_worker_id: Optional[int] = None


class AppointmentResponse(BaseModel):
    id: int
    scheduled_datetime: datetime
    doctor_name: Optional[str]
    specialty: Optional[str]
    address: str
    description: Optional[str]
    status: str
    doctors_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    elderly_id: int
    health_worker_id: int

    class Config:
        from_attributes = True

