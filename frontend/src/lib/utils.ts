import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format periodicity in minutes to a human-readable string
 */
export function formatPeriodicity(minutes: number | null | undefined): string {
  if (!minutes) return "Una vez"
  
  if (minutes < 60) {
    return `Cada ${minutes} minuto${minutes > 1 ? 's' : ''}`
  }
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (remainingMinutes === 0) {
    if (hours === 24) {
      return "Diario"
    }
    return `Cada ${hours} hora${hours > 1 ? 's' : ''}`
  }
  
  if (hours === 24 && remainingMinutes === 0) {
    return "Diario"
  }
  
  return `Cada ${hours}h ${remainingMinutes}m`
}

/**
 * Format periodicity from common strings to minutes
 */
export function parsePeriodicityToMinutes(periodicity: string): number | null {
  const lower = periodicity.toLowerCase()
  
  if (lower.includes("diario") || lower.includes("daily")) {
    return 1440 // 24 hours
  }
  
  if (lower.includes("8 horas") || lower.includes("8 hours")) {
    return 480 // 8 hours
  }
  
  if (lower.includes("12 horas") || lower.includes("12 hours")) {
    return 720 // 12 hours
  }
  
  if (lower.includes("2 días") || lower.includes("2 days")) {
    return 2880 // 48 hours
  }
  
  if (lower.includes("semanal") || lower.includes("weekly")) {
    return 10080 // 7 days
  }
  
  // Try to extract number
  const match = periodicity.match(/(\d+)/)
  if (match) {
    const num = parseInt(match[1])
    if (lower.includes("hora") || lower.includes("hour")) {
      return num * 60
    }
    if (lower.includes("minuto") || lower.includes("minute")) {
      return num
    }
  }
  
  return null
}

