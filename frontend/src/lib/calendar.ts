import { api } from './api'
import type { CalendarEvent } from '@/app/components/calendar/types'
import type { ReminderInstance } from '@/app/components/reminders/components/types'

/**
 * Convert ReminderInstance to CalendarEvent
 */
export function reminderInstanceToCalendarEvent(instance: ReminderInstance): CalendarEvent {
  const date = new Date(instance.scheduled_datetime)
  
  return {
    id: instance.id.toString(),
    date: date.getDate(),
    title: instance.medicine_name || 'Medicina',
    time: date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
    type: 'medicine',
    description: instance.dosage || '',
    status: instance.status === 'success' ? 'success' : instance.status === 'failed' ? 'failed' : 'pending',
    retries: instance.retry_count ?? 0,
    maxRetries: instance.max_retries ?? 3,
    contactMethod: instance.method || 'whatsapp',
    duration: 15, // Default duration
  }
}

/**
 * Fetch calendar events for a given month (optimized - single API call with date filter)
 */
export async function getCalendarEventsForMonth(year: number, month: number): Promise<CalendarEvent[]> {
  try {
    const instances = await api.getMonthReminderInstancesWithMedicine(year, month + 1) // month is 0-indexed in JS, backend expects 1-indexed
    return instances.map(reminderInstanceToCalendarEvent)
  } catch (error) {
    console.error('Error fetching calendar events:', error)
    return []
  }
}

/**
 * Get events for a specific day
 */
export function getEventsForDay(events: CalendarEvent[], day: number): CalendarEvent[] {
  return events.filter((event) => event.date === day)
}

