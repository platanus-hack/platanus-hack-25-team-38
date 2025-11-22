"use client"

import { TimelineItem } from "./timeline-item"
import { TimelineItemSkeleton } from "./timeline-item-skeleton"
import { ReminderInstance } from "./types"

interface TodayTabProps {
  reminderInstances: ReminderInstance[]
  loading?: boolean
}

export function TodayTab({ reminderInstances, loading = false }: TodayTabProps) {
  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="max-w-3xl mx-auto">
        <h3 className="text-lg font-semibold text-foreground mb-6">
          Recordatorios de hoy -{" "}
          {new Date().toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long" })}
        </h3>

        <div className="relative space-y-6">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border"></div>

          {loading ? (
            <>
              {Array.from({ length: 3 }).map((_, i) => (
                <TimelineItemSkeleton key={i} />
              ))}
            </>
          ) : reminderInstances.length > 0 ? (
            reminderInstances.map((instance) => (
              <TimelineItem key={instance.id} instance={instance} />
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <p className="text-muted-foreground">No hay recordatorios para hoy</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
