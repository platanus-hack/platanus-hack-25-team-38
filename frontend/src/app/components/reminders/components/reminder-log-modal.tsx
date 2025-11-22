"use client"

import React from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { ReminderInstance } from "./types"

interface LogEntry {
  id: string
  time: string
  status: string
  note?: string
}

interface ReminderLogModalProps {
  isOpen: boolean
  onClose: () => void
  instance: ReminderInstance
}

function format(dt?: string) {
  if (!dt) return new Date().toLocaleString("es-ES")
  const d = new Date(dt)
  return d.toLocaleString("es-ES")
}

export function ReminderLogModal({ isOpen, onClose, instance }: ReminderLogModalProps) {
  // build a simple mock log from instance data for demonstration
  const entries: LogEntry[] = []

  // initial send
  entries.push({ id: "e1", time: format(instance.scheduled_datetime), status: "Recordatorio enviado (primer intento)", note: `Método: ${instance.method}` })

  // retries
  for (let i = 1; i <= instance.retry_count; i++) {
    entries.push({ id: `r${i}`, time: format(), status: `Recordatorio enviado (reintento ${i})`, note: `Método: ${instance.method}` })
  }

  // waiting
  if (instance.status === "pending") {
    entries.push({ id: "w1", time: format(), status: "A la espera de confirmación" })
    entries.push({ id: "w2", time: format(), status: "Sin respuesta" })
  }

  if (instance.status === "success") {
    entries.push({ id: "s1", time: format(instance.taken_at || undefined), status: "Confirmado → Tomado" })
  }

  if (instance.status === "failed") {
    entries.push({ id: "f1", time: format(), status: "Confirmado → No tomado" })
    entries.push({ id: "es1", time: format(), status: "Escalado a familia" })
  }

  entries.push({ id: "c1", time: format(), status: "Cierre de toma" })

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose() }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Historial - {instance.medicine_name}</DialogTitle>
        </DialogHeader>

        <div className="space-y-3 mt-2">
          {entries.map((e) => (
            <div key={e.id} className="p-3 bg-muted rounded-md">
              <div className="text-xs text-muted-foreground">{e.time}</div>
              <div className="font-medium">{e.status}</div>
              {e.note && <div className="text-xs text-muted-foreground">{e.note}</div>}
            </div>
          ))}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cerrar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ReminderLogModal
