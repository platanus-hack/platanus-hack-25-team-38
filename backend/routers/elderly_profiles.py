from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.elderly_profiles import ElderlyProfileService
from dtos.elderly_profiles import ElderlyProfileCreate, ElderlyProfileUpdate, ElderlyProfileResponse

router = APIRouter(prefix="/elderly-profiles", tags=["elderly-profiles"])


@router.get("/", response_model=List[ElderlyProfileResponse])
async def get_elderly_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los perfiles de adultos mayores con paginación"""
    profiles = ElderlyProfileService.get_all(db, skip=skip, limit=limit)
    return profiles


@router.get("/{profile_id}", response_model=ElderlyProfileResponse)
async def get_elderly_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un perfil por su ID"""
    profile = ElderlyProfileService.get_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Perfil con ID {profile_id} no encontrado"
        )
    return profile


@router.post("/", response_model=ElderlyProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_elderly_profile(
    profile_data: ElderlyProfileCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo perfil de adulto mayor"""
    try:
        profile = ElderlyProfileService.create(db, profile_data)
        return profile
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


@router.put("/{profile_id}", response_model=ElderlyProfileResponse)
async def update_elderly_profile(
    profile_id: int,
    profile_data: ElderlyProfileUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un perfil existente"""
    try:
        profile = ElderlyProfileService.update(db, profile_id, profile_data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil con ID {profile_id} no encontrado"
            )
        return profile
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


@router.patch("/{profile_id}", response_model=ElderlyProfileResponse)
async def partial_update_elderly_profile(
    profile_id: int,
    profile_data: ElderlyProfileUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar parcialmente un perfil existente"""
    try:
        profile = ElderlyProfileService.update(db, profile_id, profile_data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil con ID {profile_id} no encontrado"
            )
        return profile
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


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_elderly_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un perfil"""
    success = ElderlyProfileService.delete(db, profile_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Perfil con ID {profile_id} no encontrado"
        )
    return None

