from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from models import Reminder, ReminderInstance, Appointment, Medicine, ElderlyProfile, NotificationLog
from services.reminder_instances import ReminderInstanceService
from services.notification_logs import NotificationLogService
from dtos.reminder_instances import ReminderInstanceCreate
from dtos.notification_logs import NotificationLogCreate
from enums import ReminderInstanceStatus
from integrations.kapso import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)


class ReminderSchedulerService:
    @staticmethod
    def calculate_next_scheduled_datetime(
        db: Session, reminder: Reminder
    ) -> Optional[datetime]:
        """
        Calcula el próximo scheduled_datetime basado en:
        - start_date del reminder
        - periodicity (minutos entre recordatorios)
        - Número de reminder_instances ya creadas para ese reminder
        """
        if not reminder.is_active:
            return None
        
        now = datetime.now()
        
        # Si start_date es en el futuro, no hay nada que procesar aún
        if reminder.start_date > now:
            return None
        
        # Si hay end_date y ya pasó, no crear más instancias
        if reminder.end_date:
            end_datetime = datetime.combine(reminder.end_date, datetime.max.time())
            if end_datetime < now:
                return None
        
        # Verificar si ya existe una instancia para este reminder
        # Buscar la instancia más reciente para este reminder
        existing_instance = db.query(ReminderInstance).filter(
            ReminderInstance.reminder_id == reminder.id
        ).order_by(ReminderInstance.scheduled_datetime.desc()).first()
        
        # Si periodicity es None o 0, solo se envía una vez
        if not reminder.periodicity or reminder.periodicity == 0:
            if not existing_instance:
                return reminder.start_date
            return None
        
        # Calcular el próximo scheduled_datetime
        if existing_instance:
            # Si ya existe una instancia, el próximo es su scheduled_datetime + periodicity
            next_datetime = existing_instance.scheduled_datetime + timedelta(minutes=reminder.periodicity)
        else:
            # Si no existe, el primero es start_date
            next_datetime = reminder.start_date
        
        # Si el próximo datetime ya pasó, retornarlo
        if next_datetime <= now:
            return next_datetime
        
        return None
    
    @staticmethod
    def get_reminders_to_process(db: Session) -> List[Reminder]:
        """
        Obtiene reminders activos que deben procesarse ahora
        """
        now = datetime.now()
        active_reminders = db.query(Reminder).filter(
            Reminder.is_active.is_(True),
            Reminder.start_date <= now
        ).all()
        
        reminders_to_process = []
        for reminder in active_reminders:
            next_datetime = ReminderSchedulerService.calculate_next_scheduled_datetime(db, reminder)
            if next_datetime is None:
                continue
            
            # Verificar que no exista ya un reminder_instance para ese momento exacto
            existing_instance = db.query(ReminderInstance).filter(
                and_(
                    ReminderInstance.reminder_id == reminder.id,
                    ReminderInstance.scheduled_datetime == next_datetime
                )
            ).first()
            
            if not existing_instance:
                reminders_to_process.append((reminder, next_datetime))
        
        return reminders_to_process
    
    @staticmethod
    def get_emergency_contact(
        db: Session, reminder: Reminder
    ) -> Optional[str]:
        """
        Obtiene el emergency_contact según el reminder_type
        """
        if reminder.reminder_type == "appointment":
            # reminder.appointment_id es FK a appointments.id
            if not reminder.appointment_id:
                logger.error(f"Reminder {reminder.id} de tipo appointment no tiene appointment_id")
                return None
            
            appointment = db.query(Appointment).filter(Appointment.id == reminder.appointment_id).first()
            if not appointment:
                logger.error(f"Appointment con ID {reminder.appointment_id} no encontrado")
                return None
            
            elderly_profile = db.query(ElderlyProfile).filter(
                ElderlyProfile.id == appointment.elderly_id
            ).first()
            
            if not elderly_profile:
                logger.error(f"ElderlyProfile con ID {appointment.elderly_id} no encontrado")
                return None
            
            return elderly_profile.emergency_contact
        
        elif reminder.reminder_type == "medicine":
            # reminder.medicine es FK a medicines.id
            if not reminder.medicine:
                logger.error(f"Reminder {reminder.id} de tipo medicine no tiene campo medicine")
                return None
            
            medicine = db.query(Medicine).filter(Medicine.id == reminder.medicine).first()
            if not medicine:
                logger.error(f"Medicine con ID {reminder.medicine} no encontrado")
                return None
            
            # medicine.id es FK a elderly_profiles.id
            elderly_profile = db.query(ElderlyProfile).filter(
                ElderlyProfile.id == medicine.id
            ).first()
            
            if not elderly_profile:
                logger.error(f"ElderlyProfile con ID {medicine.id} no encontrado")
                return None
            
            return elderly_profile.emergency_contact
        
        # Otros tipos de reminder no implementados por ahora
        logger.warning(f"Tipo de reminder '{reminder.reminder_type}' no implementado")
        return None
    
    @staticmethod
    def create_whatsapp_message(reminder: Reminder) -> tuple[str, list]:
        """
        Crea el mensaje de WhatsApp apropiado según el tipo de reminder
        Retorna: (mensaje, botones)
        """
        if reminder.reminder_type == "medicine":
            message = "Recordatorio: Es hora de tomar tu medicamento. Por favor confirma cuando lo hayas tomado."
            buttons = [
                {"id": "taken", "title": "Ya lo tomé"},
                {"id": "skip", "title": "Omitir"}
            ]
        elif reminder.reminder_type == "appointment":
            message = "Recordatorio: Tienes una cita médica próximamente. Por favor confirma tu asistencia."
            buttons = [
                {"id": "confirm", "title": "Confirmar"},
                {"id": "cancel", "title": "Cancelar"}
            ]
        else:
            message = "Tienes un recordatorio pendiente. Por favor confirma."
            buttons = [
                {"id": "confirm", "title": "Confirmar"},
                {"id": "dismiss", "title": "Descartar"}
            ]
        
        return message, buttons
    
    @staticmethod
    async def process_reminder(
        db: Session, reminder: Reminder, scheduled_datetime: datetime
    ) -> Dict:
        """
        Procesa un reminder: crea reminder_instance, envía WhatsApp y actualiza estados
        """
        result = {
            "reminder_id": reminder.id,
            "success": False,
            "error": None
        }
        
        try:
            # Obtener emergency_contact
            emergency_contact = ReminderSchedulerService.get_emergency_contact(db, reminder)
            if not emergency_contact:
                error_msg = f"No se pudo obtener emergency_contact para reminder {reminder.id}"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Verificar si ya existe una instancia para este reminder y scheduled_datetime
            existing_instance = db.query(ReminderInstance).filter(
                and_(
                    ReminderInstance.reminder_id == reminder.id,
                    ReminderInstance.scheduled_datetime == scheduled_datetime
                )
            ).first()
            
            if existing_instance:
                # Actualizar instancia existente
                from dtos.reminder_instances import ReminderInstanceUpdate
                instance_update = ReminderInstanceUpdate(
                    scheduled_datetime=scheduled_datetime,
                    status=ReminderInstanceStatus.PENDING.value
                )
                reminder_instance = ReminderInstanceService.update(db, existing_instance.id, instance_update)
                if not reminder_instance:
                    reminder_instance = existing_instance
            else:
                # Crear nueva instancia
                # Necesitamos generar un ID único - usar el máximo ID + 1
                max_id_result = db.query(func.max(ReminderInstance.id)).scalar()
                next_id = (max_id_result or 0) + 1
                
                instance_data = ReminderInstanceCreate(
                    id=next_id,
                    reminder_id=reminder.id,
                    scheduled_datetime=scheduled_datetime,
                    status=ReminderInstanceStatus.PENDING.value
                )
                
                try:
                    reminder_instance = ReminderInstanceService.create(db, instance_data)
                    logger.info(f"ReminderInstance creado con id={reminder_instance.id if reminder_instance else None}")
                except Exception as e:
                    db.rollback()
                    error_msg = f"Error al crear reminder_instance para reminder {reminder.id}: {str(e)}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
                
                # Validar que la instancia se creó correctamente
                if not reminder_instance:
                    db.rollback()
                    error_msg = f"No se pudo crear reminder_instance para reminder {reminder.id}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
                
                # Verificar que tiene ID válido
                if not reminder_instance.id:
                    db.rollback()
                    error_msg = f"ReminderInstance creado pero sin ID válido para reminder {reminder.id}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
                
                logger.info(f"ReminderInstance {reminder_instance.id} creado, listo para crear notification_log")
            
            # Validar que reminder_instance existe antes de crear notification_log
            if not reminder_instance or not reminder_instance.id:
                error_msg = f"ReminderInstance inválido para reminder {reminder.id}"
                logger.error(error_msg)
                result["error"] = error_msg
                return result
            
            # Asegurar que el reminder_instance está visible en la base de datos
            # ReminderInstanceService.create ya hizo commit, pero refrescamos para sincronizar
            db.refresh(reminder_instance)
            
            # Verificar que no existe ya un notification_log con ese ID
            existing_log = db.query(NotificationLog).filter(NotificationLog.id == reminder_instance.id).first()
            if existing_log:
                logger.warning(f"Ya existe un notification_log con id={reminder_instance.id}, usando el existente")
                notification_log = existing_log
            else:
                # Crear notification_log inicial
                # El reminder_instance ya existe y está confirmado en la base de datos
                message, buttons = ReminderSchedulerService.create_whatsapp_message(reminder)
                log_data = NotificationLogCreate(
                    id=reminder_instance.id,
                    reminder_instance_id=reminder_instance.id,
                    notification_type="whatsapp",
                    recepient_phone=emergency_contact,
                    status="pending",
                    sent_at=datetime.now()
                )
                
                try:
                    notification_log = NotificationLogService.create(db, log_data)
                    # Hacer commit después de crear ambos objetos (reminder_instance y notification_log)
                    db.commit()
                    if not notification_log:
                        db.rollback()
                        error_msg = f"No se pudo crear notification_log para reminder_instance {reminder_instance.id}"
                        logger.error(error_msg)
                        result["error"] = error_msg
                        return result
                    logger.info(f"NotificationLog creado exitosamente con id={notification_log.id}, reminder_instance_id={notification_log.reminder_instance_id}")
                except Exception as e:
                    db.rollback()
                    error_msg = f"Error al crear notification_log para reminder_instance {reminder_instance.id}: {str(e)}"
                    logger.error(error_msg)
                    result["error"] = error_msg
                    return result
            
            # Enviar WhatsApp
            try:
                await send_whatsapp_message(
                    to=emergency_contact,
                    body_text=message,
                    buttons=buttons
                )
                
                # Actualizar reminder_instance a "waiting"
                from dtos.reminder_instances import ReminderInstanceUpdate
                instance_update = ReminderInstanceUpdate(
                    status=ReminderInstanceStatus.WAITING.value
                )
                ReminderInstanceService.update(db, reminder_instance.id, instance_update)
                
                # Actualizar notification_log con información del envío
                from dtos.notification_logs import NotificationLogUpdate
                log_update = NotificationLogUpdate(
                    status="sent",
                    sent_at=datetime.now()
                )
                NotificationLogService.update(db, notification_log.id, log_update)
                
                result["success"] = True
                logger.info(f"Reminder {reminder.id} procesado exitosamente. WhatsApp enviado a {emergency_contact}")
                
            except Exception as e:
                error_msg = f"Error al enviar WhatsApp: {str(e)}"
                logger.error(error_msg)
                
                # Actualizar reminder_instance a "failure"
                from dtos.reminder_instances import ReminderInstanceUpdate
                instance_update = ReminderInstanceUpdate(
                    status=ReminderInstanceStatus.FAILURE.value
                )
                ReminderInstanceService.update(db, reminder_instance.id, instance_update)
                
                # Actualizar notification_log con el error
                from dtos.notification_logs import NotificationLogUpdate
                log_update = NotificationLogUpdate(
                    status="failed",
                    error_message=error_msg
                )
                NotificationLogService.update(db, notification_log.id, log_update)
                
                result["error"] = error_msg
                
        except Exception as e:
            error_msg = f"Error al procesar reminder {reminder.id}: {str(e)}"
            logger.error(error_msg)
            result["error"] = error_msg
        
        return result
    
    @staticmethod
    async def process_pending_reminders(db: Session) -> Dict:
        """
        Procesa todos los reminders pendientes
        Retorna estadísticas del procesamiento
        """
        reminders_to_process = ReminderSchedulerService.get_reminders_to_process(db)
        
        results = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for reminder, scheduled_datetime in reminders_to_process:
            result = await ReminderSchedulerService.process_reminder(db, reminder, scheduled_datetime)
            results["processed"] += 1
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                if result["error"]:
                    results["errors"].append({
                        "reminder_id": result["reminder_id"],
                        "error": result["error"]
                    })
        
        return results

