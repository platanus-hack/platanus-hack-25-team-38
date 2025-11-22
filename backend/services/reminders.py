from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from models import Reminder, Appointment, ElderlyProfile, Medicine  # Importar todas las tablas referenciadas
from dtos.reminders import ReminderCreate, ReminderUpdate, ReminderWithMedicineResponse
from dtos.medicines import MedicineResponse


class ReminderService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Reminder]:
        """Obtener todos los recordatorios con paginación"""
        return db.query(Reminder).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, reminder_id: int) -> Optional[Reminder]:
        """Obtener un recordatorio por su ID"""
        return db.query(Reminder).filter(Reminder.id == reminder_id).first()

    @staticmethod
    def get_active(db: Session) -> List[Reminder]:
        """Obtener todos los recordatorios activos"""
        return db.query(Reminder).filter(Reminder.is_active == True).all()

    @staticmethod
    def get_by_type(db: Session, reminder_type: str) -> List[Reminder]:
        """Obtener todos los recordatorios por tipo"""
        return db.query(Reminder).filter(Reminder.reminder_type == reminder_type).all()

    @staticmethod
    def create(db: Session, reminder_data: ReminderCreate) -> Reminder:
        """Crear un nuevo recordatorio"""
        reminder = Reminder(**reminder_data.model_dump())
        db.add(reminder)
        try:
            db.commit()
            db.refresh(reminder)
            return reminder
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower() or 'violates foreign key constraint' in error_msg.lower():
                # Mensaje más específico basado en el error de la BD
                if 'medicine' in error_msg.lower() and reminder_data.medicine:
                    raise ValueError(f"Error: Medicine con ID {reminder_data.medicine} no existe")
                elif 'appointment' in error_msg.lower() and reminder_data.appointment_id:
                    raise ValueError(f"Error: Appointment con ID {reminder_data.appointment_id} no existe")
                elif 'elderly_profile' in error_msg.lower() and reminder_data.elderly_profile_id:
                    raise ValueError(f"Error: ElderlyProfile con ID {reminder_data.elderly_profile_id} no existe")
                raise ValueError(
                    f"Error: Una de las foreign keys no existe. "
                    f"Detalle: {error_msg}"
                )
            raise ValueError(f"Error al crear el recordatorio: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al crear el recordatorio: {str(e)}")

    @staticmethod
    def update(
        db: Session, reminder_id: int, reminder_data: ReminderUpdate
    ) -> Optional[Reminder]:
        """Actualizar un recordatorio existente"""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None

        update_data = reminder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)

        try:
            db.commit()
            db.refresh(reminder)
            return reminder
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Error al actualizar el recordatorio: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al actualizar el recordatorio: {str(e)}")

    @staticmethod
    def delete(db: Session, reminder_id: int) -> bool:
        """Eliminar un recordatorio"""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return False

        db.delete(reminder)
        db.commit()
        return True

    @staticmethod
    def get_all_with_medicine(db: Session, skip: int = 0, limit: int = 100) -> List[ReminderWithMedicineResponse]:
        """Obtener todos los recordatorios con datos de medicina usando join"""
        reminders = (
            db.query(Reminder, Medicine)
            .outerjoin(Medicine, Reminder.medicine == Medicine.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for reminder, medicine in reminders:
            medicine_data = None
            if medicine:
                medicine_data = MedicineResponse(
                    id=medicine.id,
                    name=medicine.name,
                    dosage=medicine.dosage,
                    total_tablets=medicine.total_tablets,
                    tablets_left=medicine.tablets_left,
                    tablets_per_dose=medicine.tablets_per_dose,
                    notes=medicine.notes,
                    created_at=medicine.created_at,
                    updated_at=medicine.updated_at,
                )
            
            reminder_response = ReminderWithMedicineResponse(
                id=reminder.id,
                reminder_type=reminder.reminder_type,
                periodicity=reminder.periodicity,
                start_date=reminder.start_date,
                end_date=reminder.end_date,
                medicine=reminder.medicine,
                appointment_id=reminder.appointment_id,
                elderly_profile_id=reminder.elderly_profile_id,
                is_active=reminder.is_active,
                created_at=reminder.created_at,
                updated_at=reminder.updated_at,
                medicineData=medicine_data
            )
            result.append(reminder_response)
        
        return result

    @staticmethod
    def get_active_with_medicine(db: Session) -> List[ReminderWithMedicineResponse]:
        """Obtener todos los recordatorios activos con datos de medicina usando join"""
        reminders = (
            db.query(Reminder, Medicine)
            .outerjoin(Medicine, Reminder.medicine == Medicine.id)
            .filter(Reminder.is_active == True)
            .all()
        )
        
        result = []
        for reminder, medicine in reminders:
            medicine_data = None
            if medicine:
                medicine_data = MedicineResponse(
                    id=medicine.id,
                    name=medicine.name,
                    dosage=medicine.dosage,
                    total_tablets=medicine.total_tablets,
                    tablets_left=medicine.tablets_left,
                    tablets_per_dose=medicine.tablets_per_dose,
                    notes=medicine.notes,
                    created_at=medicine.created_at,
                    updated_at=medicine.updated_at,
                )
            
            reminder_response = ReminderWithMedicineResponse(
                id=reminder.id,
                reminder_type=reminder.reminder_type,
                periodicity=reminder.periodicity,
                start_date=reminder.start_date,
                end_date=reminder.end_date,
                medicine=reminder.medicine,
                appointment_id=reminder.appointment_id,
                elderly_profile_id=reminder.elderly_profile_id,
                is_active=reminder.is_active,
                created_at=reminder.created_at,
                updated_at=reminder.updated_at,
                medicineData=medicine_data
            )
            result.append(reminder_response)
        
        return result

