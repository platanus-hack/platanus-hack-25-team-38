"use client"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { AlertCircle } from "lucide-react"
import { Reminder } from "./types"

interface DeleteConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  reminder: Reminder | null
  onConfirm: () => void
  loading?: boolean
}

export function DeleteConfirmationModal({
  isOpen,
  onClose,
  reminder,
  onConfirm,
  loading = false,
}: DeleteConfirmationModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            Eliminar Recordatorio
          </DialogTitle>
        </DialogHeader>
        <div className="py-4">
          <p className="text-foreground">
            ¿Estás seguro de que deseas eliminar el recordatorio de{" "}
            <strong>{reminder?.medicineData?.name || "esta medicina"}</strong>?
          </p>
          <p className="text-sm text-muted-foreground mt-2">Esta acción no se puede deshacer.</p>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button variant="destructive" onClick={onConfirm} loading={loading}>
            Eliminar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
