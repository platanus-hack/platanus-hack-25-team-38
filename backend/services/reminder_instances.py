from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func, cast, Date
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from models import ReminderInstance, Reminder, Medicine
from dtos.reminder_instances import ReminderInstanceCreate, ReminderInstanceUpdate, ReminderInstanceWithMedicineResponse


class ReminderInstanceService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ReminderInstance]:
        """Obtener todas las instancias de recordatorios con paginación"""
        return db.query(ReminderInstance).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, instance_id: int) -> Optional[ReminderInstance]:
        """Obtener una instancia de recordatorio por su ID"""
        return db.query(ReminderInstance).filter(ReminderInstance.id == instance_id).first()

    @staticmethod
    def get_by_reminder_id(db: Session, reminder_id: int) -> List[ReminderInstance]:
        """Obtener todas las instancias de un recordatorio"""
        return db.query(ReminderInstance).filter(ReminderInstance.reminder_id == reminder_id).all()

    @staticmethod
    def get_by_status(db: Session, status: str) -> List[ReminderInstance]:
        """Obtener todas las instancias por estado"""
        return db.query(ReminderInstance).filter(ReminderInstance.status == status).all()

    @staticmethod
    def get_pending(db: Session) -> List[ReminderInstance]:
        """Obtener todas las instancias pendientes"""
        return db.query(ReminderInstance).filter(ReminderInstance.status == "pending").all()

    @staticmethod
    def create(db: Session, instance_data: ReminderInstanceCreate) -> ReminderInstance:
        """Crear una nueva instancia de recordatorio"""
        # Excluir el ID del dump para que la BD lo genere automáticamente
        data = instance_data.model_dump(exclude={'id'})
        instance = ReminderInstance(**data)
        
        try:
            db.add(instance)
            db.flush()
            db.refresh(instance)
            return instance
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower() or 'violates foreign key constraint' in error_msg.lower():
                raise ValueError(f"Error: El reminder_id {instance_data.reminder_id} no existe en la tabla reminders")
            raise ValueError(f"Error al crear la instancia de recordatorio: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al crear la instancia de recordatorio: {str(e)}")

    @staticmethod
    def update(
        db: Session, instance_id: int, instance_data: ReminderInstanceUpdate
    ) -> Optional[ReminderInstance]:
        """Actualizar una instancia de recordatorio existente"""
        instance = db.query(ReminderInstance).filter(ReminderInstance.id == instance_id).first()
        if not instance:
            return None

        update_data = instance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(instance, field, value)

        try:
            db.commit()
            db.refresh(instance)
            return instance
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            raise ValueError(f"Error al actualizar la instancia de recordatorio: {error_msg}")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error inesperado al actualizar la instancia de recordatorio: {str(e)}")

    @staticmethod
    def delete(db: Session, instance_id: int) -> bool:
        """Eliminar una instancia de recordatorio"""
        instance = db.query(ReminderInstance).filter(ReminderInstance.id == instance_id).first()
        if not instance:
            return False

        db.delete(instance)
        db.commit()
        return True

    @staticmethod
    def get_all_with_medicine(db: Session, skip: int = 0, limit: int = 100) -> List[ReminderInstanceWithMedicineResponse]:
        """Obtener todas las instancias con datos de reminder y medicina usando joins"""
        instances = (
            db.query(ReminderInstance, Reminder, Medicine)
            .join(Reminder, ReminderInstance.reminder_id == Reminder.id)
            .outerjoin(Medicine, Reminder.medicine == Medicine.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for instance, reminder, medicine in instances:
            instance_response = ReminderInstanceWithMedicineResponse(
                id=instance.id,
                reminder_id=instance.reminder_id,
                scheduled_datetime=instance.scheduled_datetime,
                status=instance.status,
                taken_at=instance.taken_at,
                retry_count=instance.retry_count,
                max_retries=instance.max_retries,
                family_notified=instance.family_notified,
                family_notified_at=instance.family_notified_at,
                notes=instance.notes,
                created_at=instance.created_at,
                updated_at=instance.updated_at,
                message_id=instance.message_id,
                medicine_name=medicine.name if medicine else None,
                dosage=medicine.dosage if medicine else None,
                method=None
            )
            result.append(instance_response)
        
        return result

    @staticmethod
    def get_today_with_medicine(db: Session) -> List[ReminderInstanceWithMedicineResponse]:
        """Obtener instancias de hoy con datos de reminder y medicina usando joins"""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        start_of_tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        # Use date range for PostgreSQL - more reliable
        # Get all instances where scheduled_datetime is >= start of today and < start of tomorrow
        instances = (
            db.query(ReminderInstance, Reminder, Medicine)
            .join(Reminder, ReminderInstance.reminder_id == Reminder.id)
            .outerjoin(Medicine, Reminder.medicine == Medicine.id)
            .filter(
                and_(
                    ReminderInstance.scheduled_datetime >= start_of_day,
                    ReminderInstance.scheduled_datetime < start_of_tomorrow
                )
            )
            .order_by(ReminderInstance.scheduled_datetime.asc())
            .all()
        )
        
        result = []
        for instance, reminder, medicine in instances:
            instance_response = ReminderInstanceWithMedicineResponse(
                id=instance.id,
                reminder_id=instance.reminder_id,
                scheduled_datetime=instance.scheduled_datetime,
                status=instance.status,
                taken_at=instance.taken_at,
                retry_count=instance.retry_count,
                max_retries=instance.max_retries,
                family_notified=instance.family_notified,
                family_notified_at=instance.family_notified_at,
                notes=instance.notes,
                created_at=instance.created_at,
                updated_at=instance.updated_at,
                message_id=instance.message_id,
                medicine_name=medicine.name if medicine else None,
                dosage=medicine.dosage if medicine else None,
                method=None
            )
            result.append(instance_response)
        
        return result

    @staticmethod
    def get_by_month_with_medicine(db: Session, year: int, month: int) -> List[ReminderInstanceWithMedicineResponse]:
        """Obtener instancias de un mes específico con datos de reminder y medicina usando joins"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        instances = (
            db.query(ReminderInstance, Reminder, Medicine)
            .join(Reminder, ReminderInstance.reminder_id == Reminder.id)
            .outerjoin(Medicine, Reminder.medicine == Medicine.id)
            .filter(
                and_(
                    ReminderInstance.scheduled_datetime >= start_date,
                    ReminderInstance.scheduled_datetime < end_date
                )
            )
            .all()
        )
        
        result = []
        for instance, reminder, medicine in instances:
            instance_response = ReminderInstanceWithMedicineResponse(
                id=instance.id,
                reminder_id=instance.reminder_id,
                scheduled_datetime=instance.scheduled_datetime,
                status=instance.status,
                taken_at=instance.taken_at,
                retry_count=instance.retry_count,
                max_retries=instance.max_retries,
                family_notified=instance.family_notified,
                family_notified_at=instance.family_notified_at,
                notes=instance.notes,
                created_at=instance.created_at,
                updated_at=instance.updated_at,
                message_id=instance.message_id,
                medicine_name=medicine.name if medicine else None,
                dosage=medicine.dosage if medicine else None,
                method=None
            )
            result.append(instance_response)
        
        return result

