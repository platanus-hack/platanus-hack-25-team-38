import { api } from './api'
import type { Reminder, ReminderInstance } from '@/app/components/reminders/components/types'

/**
 * Service to fetch reminders with related medicine data
 * Now uses optimized backend endpoints with SQL joins
 */
export class RemindersService {
  /**
   * Fetch all reminders with medicine data (optimized - single API call)
   */
  static async getRemindersWithMedicine(): Promise<Reminder[]> {
    return await api.getRemindersWithMedicine() as Reminder[]
  }

  /**
   * Fetch active reminders with medicine data (optimized - single API call)
   */
  static async getActiveRemindersWithMedicine(): Promise<Reminder[]> {
    return await api.getActiveRemindersWithMedicine() as Reminder[]
  }

  /**
   * Fetch a single reminder with medicine data
   */
  static async getReminderWithMedicine(id: number): Promise<Reminder | null> {
    try {
      const reminder = await api.getReminder(id)
      // If reminder has medicine, fetch it separately (single reminder doesn't have optimized endpoint)
      if (reminder.medicine) {
        try {
          const medicineData = await api.getMedicine(reminder.medicine)
          return {
            ...reminder,
            medicineData,
          } as Reminder
        } catch (error) {
          console.error(`Failed to fetch medicine ${reminder.medicine}:`, error)
          return {
            ...reminder,
            medicineData: undefined,
          } as Reminder
        }
      }
      return reminder as Reminder
    } catch (error) {
      console.error(`Failed to fetch reminder ${id}:`, error)
      return null
    }
  }

  /**
   * Fetch reminder instances for today (optimized - single API call with date filter)
   */
  static async getTodayReminderInstances(): Promise<ReminderInstance[]> {
    return await api.getTodayReminderInstancesWithMedicine() as ReminderInstance[]
  }

  /**
   * Fetch reminder instances with medicine data (optimized - single API call with joins)
   */
  static async getReminderInstancesWithMedicine(): Promise<ReminderInstance[]> {
    return await api.getReminderInstancesWithMedicine() as ReminderInstance[]
  }
}

