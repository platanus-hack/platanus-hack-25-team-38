from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List, Optional
from models import ElderlyProfile, User  # Importar User para que esté en metadata
from dtos.elderly_profiles import ElderlyProfileCreate, ElderlyProfileUpdate


class ElderlyProfileService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ElderlyProfile]:
        """Obtener todos los perfiles de adultos mayores con paginación"""
        return db.query(ElderlyProfile).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, profile_id: int) -> Optional[ElderlyProfile]:
        """Obtener un perfil por su ID"""
        return db.query(ElderlyProfile).filter(ElderlyProfile.id == profile_id).first()

    @staticmethod
    def create(db: Session, profile_data: ElderlyProfileCreate) -> ElderlyProfile:
        """Crear un nuevo perfil de adulto mayor"""
        data = profile_data.model_dump()
        profile_id = data.pop('id')
        
        # Construir la query con OVERRIDING SYSTEM VALUE
        columns = ', '.join([f'"{k}"' for k in data.keys() if data[k] is not None])
        values = ', '.join([f':{k}' for k in data.keys() if data[k] is not None])
        params = {k: v for k, v in data.items() if v is not None}
        params['id'] = profile_id
        
        query = f"""
            INSERT INTO elderly_profiles (id, {columns}) 
            OVERRIDING SYSTEM VALUE 
            VALUES (:id, {values})
            RETURNING *
        """
        
        try:
            result = db.execute(text(query), params)
            db.commit()
            row = result.fetchone()
            # Convertir la fila a un objeto ElderlyProfile
            profile = db.query(ElderlyProfile).filter(ElderlyProfile.id == profile_id).first()
            return profile
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower() or 'violates foreign key constraint' in error_msg.lower():
                raise ValueError(f"Error: El ID {profile_data.id} no existe en la tabla users")
            raise ValueError(f"Error al crear el perfil: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al crear el perfil: {str(e)}")

    @staticmethod
    def update(
        db: Session, profile_id: int, profile_data: ElderlyProfileUpdate
    ) -> Optional[ElderlyProfile]:
        """Actualizar un perfil existente"""
        profile = db.query(ElderlyProfile).filter(ElderlyProfile.id == profile_id).first()
        if not profile:
            return None

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        try:
            db.commit()
            db.refresh(profile)
            return profile
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Error al actualizar el perfil: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al actualizar el perfil: {str(e)}")

    @staticmethod
    def delete(db: Session, profile_id: int) -> bool:
        """Eliminar un perfil"""
        profile = db.query(ElderlyProfile).filter(ElderlyProfile.id == profile_id).first()
        if not profile:
            return False

        db.delete(profile)
        db.commit()
        return True

