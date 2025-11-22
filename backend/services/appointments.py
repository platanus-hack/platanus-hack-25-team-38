from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models import Appointment, ElderlyProfile, HealthWorker  # Importar todos los modelos para que estén en metadata
from dtos.appointments import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Obtener todas las citas con paginación"""
        return db.query(Appointment).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, appointment_id: int) -> Optional[Appointment]:
        """Obtener una cita por su ID"""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    @staticmethod
    def create(db: Session, appointment_data: AppointmentCreate) -> Appointment:
        """Crear una nueva cita"""
        appointment = Appointment(**appointment_data.model_dump())
        db.add(appointment)
        try:
            db.commit()
            db.refresh(appointment)
            return appointment
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower() or 'violates foreign key constraint' in error_msg.lower():
                raise ValueError(f"Error: Los IDs proporcionados (elderly_id={appointment_data.elderly_id}, health_worker_id={appointment_data.health_worker_id}) no existen en las tablas correspondientes")
            raise ValueError(f"Error al crear la cita: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al crear la cita: {str(e)}")

    @staticmethod
    def update(
        db: Session, appointment_id: int, appointment_data: AppointmentUpdate
    ) -> Optional[Appointment]:
        """Actualizar una cita existente"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return None

        update_data = appointment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)

        try:
            db.commit()
            db.refresh(appointment)
            return appointment
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar la cita: {str(e)}")

    @staticmethod
    def delete(db: Session, appointment_id: int) -> bool:
        """Eliminar una cita"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False

        db.delete(appointment)
        db.commit()
        return True

    @staticmethod
    def get_by_elderly_id(db: Session, elderly_id: int) -> List[Appointment]:
        """Obtener todas las citas de un adulto mayor"""
        return db.query(Appointment).filter(Appointment.elderly_id == elderly_id).all()

    @staticmethod
    def get_by_health_worker_id(db: Session, health_worker_id: int) -> List[Appointment]:
        """Obtener todas las citas de un trabajador de salud"""
        return db.query(Appointment).filter(Appointment.health_worker_id == health_worker_id).all()

