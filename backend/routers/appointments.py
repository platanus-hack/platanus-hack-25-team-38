from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.appointments import AppointmentService
from dtos.appointments import AppointmentCreate, AppointmentUpdate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todas las citas con paginación"""
    appointments = AppointmentService.get_all(db, skip=skip, limit=limit)
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una cita por su ID"""
    appointment = AppointmentService.get_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    return appointment


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva cita"""
    try:
        appointment = AppointmentService.create(db, appointment_data)
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una cita existente"""
    try:
        appointment = AppointmentService.update(db, appointment_id, appointment_data)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {appointment_id} no encontrada"
            )
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def partial_update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar parcialmente una cita existente"""
    try:
        appointment = AppointmentService.update(db, appointment_id, appointment_data)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cita con ID {appointment_id} no encontrada"
            )
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una cita"""
    success = AppointmentService.delete(db, appointment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {appointment_id} no encontrada"
        )
    return None


@router.get("/elderly/{elderly_id}", response_model=List[AppointmentResponse])
async def get_appointments_by_elderly(
    elderly_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las citas de un adulto mayor"""
    appointments = AppointmentService.get_by_elderly_id(db, elderly_id)
    return appointments


@router.get("/health-worker/{health_worker_id}", response_model=List[AppointmentResponse])
async def get_appointments_by_health_worker(
    health_worker_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las citas de un trabajador de salud"""
    appointments = AppointmentService.get_by_health_worker_id(db, health_worker_id)
    return appointments

