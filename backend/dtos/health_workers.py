from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class HealthWorkerCreate(BaseModel):
    id: int  # Debe ser el mismo ID que el usuario
    profession: Optional[str] = None
    license_number: Optional[str] = None
    verification_status: Optional[str] = "pending"
    rating: Optional[Decimal] = None
    total_appointments: Optional[int] = 0


class HealthWorkerUpdate(BaseModel):
    profession: Optional[str] = None
    license_number: Optional[str] = None
    verification_status: Optional[str] = None
    rating: Optional[Decimal] = None
    total_appointments: Optional[int] = None


class HealthWorkerResponse(BaseModel):
    id: int
    profession: Optional[str]
    license_number: Optional[str]
    verification_status: Optional[str]
    rating: Optional[Decimal]
    total_appointments: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

