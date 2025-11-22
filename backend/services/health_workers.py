from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List, Optional
from models import HealthWorker, User  # Importar User para que esté en metadata
from dtos.health_workers import HealthWorkerCreate, HealthWorkerUpdate


class HealthWorkerService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[HealthWorker]:
        """Obtener todos los trabajadores de salud con paginación"""
        return db.query(HealthWorker).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, worker_id: int) -> Optional[HealthWorker]:
        """Obtener un trabajador de salud por su ID"""
        return db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()

    @staticmethod
    def create(db: Session, worker_data: HealthWorkerCreate) -> HealthWorker:
        """Crear un nuevo trabajador de salud"""
        data = worker_data.model_dump()
        worker_id = data.pop('id')
        
        # Construir la query con OVERRIDING SYSTEM VALUE
        columns = ', '.join([f'"{k}"' for k in data.keys() if data[k] is not None])
        values = ', '.join([f':{k}' for k in data.keys() if data[k] is not None])
        params = {k: v for k, v in data.items() if v is not None}
        params['id'] = worker_id
        
        query = f"""
            INSERT INTO health_workers (id, {columns}) 
            OVERRIDING SYSTEM VALUE 
            VALUES (:id, {values})
            RETURNING *
        """
        
        try:
            result = db.execute(text(query), params)
            db.commit()
            # Obtener el trabajador creado
            worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
            return worker
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower() or 'violates foreign key constraint' in error_msg.lower():
                raise ValueError(f"Error: El ID {worker_data.id} no existe en la tabla users")
            raise ValueError(f"Error al crear el trabajador de salud: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al crear el trabajador de salud: {str(e)}")

    @staticmethod
    def update(
        db: Session, worker_id: int, worker_data: HealthWorkerUpdate
    ) -> Optional[HealthWorker]:
        """Actualizar un trabajador de salud existente"""
        worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
        if not worker:
            return None

        update_data = worker_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(worker, field, value)

        try:
            db.commit()
            db.refresh(worker)
            return worker
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Error al actualizar el trabajador de salud: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al actualizar el trabajador de salud: {str(e)}")

    @staticmethod
    def delete(db: Session, worker_id: int) -> bool:
        """Eliminar un trabajador de salud"""
        worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
        if not worker:
            return False

        db.delete(worker)
        db.commit()
        return True

