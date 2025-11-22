from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.health_workers import HealthWorkerService
from dtos.health_workers import HealthWorkerCreate, HealthWorkerUpdate, HealthWorkerResponse

router = APIRouter(prefix="/health-workers", tags=["health-workers"])


@router.get("/", response_model=List[HealthWorkerResponse])
async def get_health_workers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los trabajadores de salud con paginación"""
    workers = HealthWorkerService.get_all(db, skip=skip, limit=limit)
    return workers


@router.get("/{worker_id}", response_model=HealthWorkerResponse)
async def get_health_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un trabajador de salud por su ID"""
    worker = HealthWorkerService.get_by_id(db, worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trabajador de salud con ID {worker_id} no encontrado"
        )
    return worker


@router.post("/", response_model=HealthWorkerResponse, status_code=status.HTTP_201_CREATED)
async def create_health_worker(
    worker_data: HealthWorkerCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo trabajador de salud"""
    try:
        worker = HealthWorkerService.create(db, worker_data)
        return worker
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


@router.put("/{worker_id}", response_model=HealthWorkerResponse)
async def update_health_worker(
    worker_id: int,
    worker_data: HealthWorkerUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un trabajador de salud existente"""
    try:
        worker = HealthWorkerService.update(db, worker_id, worker_data)
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trabajador de salud con ID {worker_id} no encontrado"
            )
        return worker
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


@router.patch("/{worker_id}", response_model=HealthWorkerResponse)
async def partial_update_health_worker(
    worker_id: int,
    worker_data: HealthWorkerUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar parcialmente un trabajador de salud existente"""
    try:
        worker = HealthWorkerService.update(db, worker_id, worker_data)
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trabajador de salud con ID {worker_id} no encontrado"
            )
        return worker
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


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_worker(
    worker_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un trabajador de salud"""
    success = HealthWorkerService.delete(db, worker_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trabajador de salud con ID {worker_id} no encontrado"
        )
    return None

