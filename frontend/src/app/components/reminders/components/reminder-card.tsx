"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Pill,
  Calendar,
  Clock,
  Power,
} from "lucide-react"
import { Reminder } from "./types"
import { formatPeriodicity } from "@/lib/utils"

interface ReminderCardProps {
  reminder: Reminder
  onCardClick: (reminder: Reminder) => void
  onToggleActive: (reminder: Reminder) => void
  isToggling?: boolean
}

export function ReminderCard({ reminder, onCardClick, onToggleActive, isToggling = false }: ReminderCardProps) {
  const medicine = reminder.medicineData
  const fillPercentage = medicine && medicine.total_tablets && medicine.tablets_left !== null
    ? (medicine.tablets_left / medicine.total_tablets) * 100
    : 0

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't trigger card click if clicking on the toggle button
    if ((e.target as HTMLElement).closest('button')) {
      return
    }
    onCardClick(reminder)
  }

  return (
    <Card 
      className="p-6 hover:shadow-md transition-shadow cursor-pointer" 
      onClick={handleCardClick}
    >
      <div className="flex gap-6">
        <div className="flex flex-col items-center gap-3">
          <div className="relative w-24 h-32 bg-gradient-to-b from-muted/30 to-muted/50 rounded-2xl border-2 border-primary flex items-end justify-center overflow-hidden shadow-sm">
            {medicine && (
              <>
                <div
                  className="w-full bg-gradient-to-b from-primary to-primary/80 transition-all duration-700"
                  style={{ height: `${fillPercentage}%` }}
                />
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <Pill
                    className={`w-10 h-10 ${fillPercentage < 30 ? "text-primary/40" : "text-white/60"}`}
                  />
                  <span
                    className={`font-bold text-lg mt-1 ${fillPercentage < 30 ? "text-primary" : "text-white"}`}
                  >
                    {medicine.tablets_left ?? 0}
                  </span>
                </div>
              </>
            )}
          </div>
          <span className="text-xs text-muted-foreground font-medium">
            de {medicine?.total_tablets ?? 0}
          </span>
        </div>

        {/* Medicine Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-xl font-bold text-foreground">{medicine?.name || "Sin medicina"}</h3>
              <p className="text-sm text-muted-foreground mt-0.5">{medicine?.dosage || ""}</p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                reminder.is_active
                  ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                  : "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400"
              }`}
            >
              {reminder.is_active ? "Activo" : "Inactivo"}
            </span>
          </div>

          <div className="flex gap-4 mb-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              <span>{formatPeriodicity(reminder.periodicity)}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Pill className="w-4 h-4" />
              <span>{medicine?.tablets_per_dose ?? 1}x dosis</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4" />
              <span>
                {new Date(reminder.start_date).toLocaleDateString("es-ES", {
                  month: "short",
                  day: "numeric",
                })}
              </span>
            </div>
          </div>

        </div>

        <div className="flex flex-col gap-2">
          <Button
            variant={reminder.is_active ? "outline" : "default"}
            size="sm"
            loading={isToggling}
            onClick={(e) => {
              e.stopPropagation()
              onToggleActive(reminder)
            }}
          >
            <Power className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}
