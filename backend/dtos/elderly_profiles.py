from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class ElderlyProfileCreate(BaseModel):
    id: int  # Debe ser el mismo ID que el usuario
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_notes: Optional[str] = None
    blood_type: Optional[str] = None
    insurance_info: Optional[str] = None
    isapre_info: Optional[str] = None


class ElderlyProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_notes: Optional[str] = None
    blood_type: Optional[str] = None
    insurance_info: Optional[str] = None
    isapre_info: Optional[str] = None


class ElderlyProfileResponse(BaseModel):
    id: int
    date_of_birth: Optional[date]
    address: Optional[str]
    emergency_contact: Optional[str]
    medical_notes: Optional[str]
    blood_type: Optional[str]
    insurance_info: Optional[str]
    isapre_info: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

