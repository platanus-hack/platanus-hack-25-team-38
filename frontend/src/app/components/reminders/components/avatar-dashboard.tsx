"use client"

import React from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ReminderInstance } from "./types"

interface AvatarDashboardProps {
  reminders: ReminderInstance[]
  onMarkAllDone?: () => void
  loading?: boolean
}


export function AvatarDashboard({ reminders, onMarkAllDone, loading = false }: AvatarDashboardProps) {
  const total = reminders.length
  const done = reminders.filter((r) => r.status === "success").length
  const pending = total - done

  return (
    <Card className="w-full p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="text-lg font-semibold">Resumen</h4>
          <p className="text-xs text-muted-foreground">Hoy</p>
        </div>
        <div>
          <Button 
            size="sm" 
            onClick={onMarkAllDone} 
            className="bg-primary hover:bg-primary/90"
            disabled={loading || pending === 0}
          >
            {loading ? "Guardando..." : "Marcar todos como tomados"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Total</div>
          <div className="font-bold text-lg">{total}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Completados</div>
          <div className="font-bold text-lg text-green-600">{done}</div>
        </div>
        <div className="text-center">
          <div className="text-sm text-muted-foreground">Pendientes</div>
          <div className="font-bold text-lg text-pink-600">{pending}</div>
        </div>
      </div>
    </Card>
  )
}

export default AvatarDashboard