import { api } from './api'
import type { Reminder, ReminderResponse, MedicineResponse, ReminderInstanceResponse } from '@/app/components/reminders/components/types'

/**
 * Service to fetch reminders with related medicine data
 */
export class RemindersService {
  /**
   * Fetch all reminders and enrich with medicine data
   */
  static async getRemindersWithMedicine(): Promise<Reminder[]> {
    const reminders = await api.getReminders() as ReminderResponse[]
    
    // Fetch medicine data for each reminder
    const enrichedReminders = await Promise.all(
      reminders.map(async (reminder) => {
        let medicineData: MedicineResponse | undefined
        
        if (reminder.medicine) {
          try {
            medicineData = await api.getMedicine(reminder.medicine) as MedicineResponse
          } catch (error) {
            console.error(`Failed to fetch medicine ${reminder.medicine}:`, error)
          }
        }
        
        return {
          ...reminder,
          medicineData,
        } as Reminder
      })
    )
    
    return enrichedReminders
  }

  /**
   * Fetch active reminders with medicine data
   */
  static async getActiveRemindersWithMedicine(): Promise<Reminder[]> {
    const reminders = await api.getActiveReminders() as ReminderResponse[]
    
    const enrichedReminders = await Promise.all(
      reminders.map(async (reminder) => {
        let medicineData: MedicineResponse | undefined
        
        if (reminder.medicine) {
          try {
            medicineData = await api.getMedicine(reminder.medicine) as MedicineResponse
          } catch (error) {
            console.error(`Failed to fetch medicine ${reminder.medicine}:`, error)
          }
        }
        
        return {
          ...reminder,
          medicineData,
        } as Reminder
      })
    )
    
    return enrichedReminders
  }

  /**
   * Fetch a single reminder with medicine data
   */
  static async getReminderWithMedicine(id: number): Promise<Reminder | null> {
    try {
      const reminder = await api.getReminder(id) as ReminderResponse
      
      let medicineData: MedicineResponse | undefined
      if (reminder.medicine) {
        try {
          medicineData = await api.getMedicine(reminder.medicine) as MedicineResponse
        } catch (error) {
          console.error(`Failed to fetch medicine ${reminder.medicine}:`, error)
        }
      }
      
      return {
        ...reminder,
        medicineData,
      } as Reminder
    } catch (error) {
      console.error(`Failed to fetch reminder ${id}:`, error)
      return null
    }
  }

  /**
   * Fetch reminder instances for today
   */
  static async getTodayReminderInstances(): Promise<ReminderInstanceResponse[]> {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    const instances = await api.getReminderInstances() as ReminderInstanceResponse[]
    
    // Filter instances for today
    return instances.filter((instance) => {
      const instanceDate = new Date(instance.scheduled_datetime)
      return instanceDate >= today && instanceDate < tomorrow
    })
  }

  /**
   * Fetch reminder instances with medicine data
   */
  static async getReminderInstancesWithMedicine(): Promise<any[]> {
    const instances = await api.getReminderInstances() as ReminderInstanceResponse[]
    
    // Fetch reminder and medicine data for each instance
    const enrichedInstances = await Promise.all(
      instances.map(async (instance) => {
        try {
          const reminder = await api.getReminder(instance.reminder_id) as ReminderResponse
          let medicineData: MedicineResponse | undefined
          
          if (reminder.medicine) {
            try {
              medicineData = await api.getMedicine(reminder.medicine) as MedicineResponse
            } catch (error) {
              console.error(`Failed to fetch medicine ${reminder.medicine}:`, error)
            }
          }
          
          return {
            ...instance,
            medicine_name: medicineData?.name || 'Unknown',
            dosage: medicineData?.dosage || '',
            method: 'whatsapp' as const, // Default, could be determined from notification_log
          }
        } catch (error) {
          console.error(`Failed to fetch reminder ${instance.reminder_id}:`, error)
          return {
            ...instance,
            medicine_name: 'Unknown',
            dosage: '',
            method: 'whatsapp' as const,
          }
        }
      })
    )
    
    return enrichedInstances
  }
}

