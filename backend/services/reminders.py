from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from models import Reminder, Appointment, ElderlyProfile, Medicine, ReminderInstance  # Importar todas las tablas referenciadas
from dtos.reminders import ReminderCreate, ReminderUpdate, ReminderWithMedicineResponse
from dtos.medicines import MedicineResponse
from dtos.reminder_instances import ReminderInstanceCreate
from enums import ReminderInstanceStatus


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
    def regenerate_future_instances(
        db: Session, reminder: Reminder
    ) -> int:
        """
        Regenera las instancias futuras de un reminder.
        Elimina todas las instancias futuras y crea nuevas basadas en:
        - start_date
        - periodicity
        - end_date (o máximo 30 iteraciones si no hay end_date)
        """
        now = datetime.now() - timedelta(hours=3)
        
        # Eliminar todas las instancias futuras (scheduled_datetime > now)
        future_instances = db.query(ReminderInstance).filter(
            and_(
                ReminderInstance.reminder_id == reminder.id,
                ReminderInstance.scheduled_datetime > now
            )
        ).all()
        
        deleted_count = len(future_instances)
        for instance in future_instances:
            db.delete(instance)
        
        # Si el reminder no está activo o no tiene periodicity, no crear nuevas instancias
        if not reminder.is_active or not reminder.periodicity or reminder.periodicity == 0:
            return deleted_count
        
        # Calcular cuántas instancias crear
        max_iterations = 30
        if reminder.end_date:
            # Calcular cuántas iteraciones caben entre start_date y end_date
            end_datetime = datetime.combine(reminder.end_date, datetime.max.time())
            time_diff = end_datetime - reminder.start_date
            iterations = int(time_diff.total_seconds() / 60 / reminder.periodicity) + 1
            max_iterations = min(iterations, 30)
        else:
            max_iterations = 30
        
        # Crear nuevas instancias
        created_count = 0
        current_datetime = reminder.start_date
        
        # Si start_date está en el pasado, comenzar desde ahora
        if current_datetime < now:
            # Calcular cuántas iteraciones ya pasaron
            time_passed = now - current_datetime
            iterations_passed = int(time_passed.total_seconds() / 60 / reminder.periodicity)
            # Avanzar al siguiente datetime futuro
            current_datetime = current_datetime + timedelta(minutes=reminder.periodicity * (iterations_passed + 1))
        
        for i in range(max_iterations):
            # Verificar si excede end_date
            if reminder.end_date:
                end_datetime = datetime.combine(reminder.end_date, datetime.max.time())
                if current_datetime > end_datetime:
                    break
            
            # Verificar que no esté en el pasado
            if current_datetime <= now:
                current_datetime = current_datetime + timedelta(minutes=reminder.periodicity)
                continue
            
            # Crear la instancia
            instance_data = ReminderInstanceCreate(
                reminder_id=reminder.id,
                scheduled_datetime=current_datetime,
                status=ReminderInstanceStatus.PENDING.value
            )
            instance = ReminderInstance(**instance_data.model_dump())
            db.add(instance)
            created_count += 1
            
            # Avanzar al siguiente datetime
            current_datetime = current_datetime + timedelta(minutes=reminder.periodicity)
        
        return deleted_count

    @staticmethod
    def update(
        db: Session, reminder_id: int, reminder_data: ReminderUpdate
    ) -> Optional[Reminder]:
        """Actualizar un recordatorio existente"""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None

        # Guardar valores antiguos para detectar cambios
        old_periodicity = reminder.periodicity
        old_start_date = reminder.start_date
        old_end_date = reminder.end_date

        update_data = reminder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)

        try:
            db.flush()  # Flush para tener los valores actualizados en memoria
            
            # Si cambió periodicity, start_date o end_date, regenerar instancias futuras
            should_regenerate = (
                (old_periodicity != reminder.periodicity) or
                (old_start_date != reminder.start_date) or
                (old_end_date != reminder.end_date)
            )
            
            if should_regenerate:
                ReminderService.regenerate_future_instances(db, reminder)
            
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

