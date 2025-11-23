"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ChevronLeft, ChevronRight, Pill, Clock, Calendar, Check } from "lucide-react"
import { api } from "@/lib/api"
import { formatPeriodicity } from "@/lib/utils"
import type { MedicineResponse } from "./types"

interface CreateReminderModalProps {
  isOpen: boolean
  onClose: () => void
}

type Step = 1 | 2 | 3 | 4

interface ReminderFormData {
  medicine: number | null
  periodicity: number | null
  startDate: string
  startTime: string
  endDate: string | null
  isActive: boolean
}

const PERIODICITY_OPTIONS = [
  { label: "Cada 8 horas", value: 480 },
  { label: "Cada 12 horas", value: 720 },
  { label: "Diario (cada 24 horas)", value: 1440 },
]

export function CreateReminderModal({ isOpen, onClose }: CreateReminderModalProps) {
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [medicines, setMedicines] = useState<MedicineResponse[]>([])
  const [loadingMedicines, setLoadingMedicines] = useState(false)
  const [formData, setFormData] = useState<ReminderFormData>({
    medicine: null,
    periodicity: null,
    startDate: new Date().toISOString().split("T")[0],
    startTime: new Date().toTimeString().slice(0, 5),
    endDate: null,
    isActive: true,
  })

  useEffect(() => {
    if (isOpen) {
      loadMedicines()
      // Reset form when opening
      setFormData({
        medicine: null,
        periodicity: null,
        startDate: new Date().toISOString().split("T")[0],
        startTime: new Date().toTimeString().slice(0, 5),
        endDate: null,
        isActive: true,
      })
      setCurrentStep(1)
    }
  }, [isOpen])

  const loadMedicines = async () => {
    setLoadingMedicines(true)
    try {
      const data = await api.getMedicines()
      setMedicines(data)
    } catch (err) {
      console.error("Error loading medicines:", err)
    } finally {
      setLoadingMedicines(false)
    }
  }

  const handleNext = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => (prev + 1) as Step)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as Step)
    }
  }

  const handleSubmit = () => {
    // Don't actually submit - just log for now
    console.log("Form data:", formData)
    onClose()
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.medicine !== null
      case 2:
        return formData.periodicity !== null
      case 3:
        return formData.startDate && formData.startTime
      case 4:
        return true
      default:
        return false
    }
  }

  const selectedMedicine = medicines.find((m) => m.id === formData.medicine)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-0">
          <DialogTitle>Crear Nuevo Recordatorio</DialogTitle>
        </DialogHeader>

        {/* Progress indicator */}
        <div className="flex items-center justify-between px-4 py-6 border-b border-border">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                    step === currentStep
                      ? "bg-primary border-primary text-primary-foreground"
                      : step < currentStep
                        ? "bg-green-500 border-green-500 text-white"
                        : "bg-background border-border text-muted-foreground"
                  }`}
                >
                  {step < currentStep ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    <span className="font-semibold">{step}</span>
                  )}
                </div>
                <span className="text-xs mt-2 text-muted-foreground">
                  {step === 1 && "Medicina"}
                  {step === 2 && "Frecuencia"}
                  {step === 3 && "Fechas"}
                  {step === 4 && "Revisar"}
                </span>
              </div>
              {step < 4 && (
                <div
                  className={`h-0.5 flex-1 mx-2 ${
                    step < currentStep ? "bg-green-500" : "bg-border"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Form content */}
        <div className="flex-1 overflow-y-auto min-h-0 px-6 py-6" style={{ maxHeight: 'calc(90vh - 280px)' }}>
          {currentStep === 1 && (
            <div className="space-y-4">
              <div>
                <Label className="text-base font-semibold mb-4 block">Selecciona una Medicina</Label>
                {loadingMedicines ? (
                  <div className="text-sm text-muted-foreground">Cargando medicinas...</div>
                ) : medicines.length === 0 ? (
                  <div className="text-sm text-muted-foreground">No hay medicinas disponibles</div>
                ) : (
                  <div className="grid gap-3">
                    {medicines.map((medicine) => (
                      <button
                        key={medicine.id}
                        onClick={() => setFormData({ ...formData, medicine: medicine.id })}
                        className={`p-4 border-2 rounded-lg text-left transition-all ${
                          formData.medicine === medicine.id
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-primary/50"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Pill className="w-6 h-6 text-primary" />
                          <div className="flex-1">
                            <div className="font-semibold text-foreground">{medicine.name}</div>
                            {medicine.dosage && (
                              <div className="text-sm text-muted-foreground">{medicine.dosage}</div>
                            )}
                          </div>
                          {formData.medicine === medicine.id && (
                            <Check className="w-5 h-5 text-primary" />
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4">
              <div>
                <Label className="text-base font-semibold mb-4 block">Frecuencia del Recordatorio</Label>
                <div className="grid gap-3">
                  {PERIODICITY_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setFormData({ ...formData, periodicity: option.value })}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        formData.periodicity === option.value
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Clock className="w-5 h-5 text-primary" />
                        <span className="font-medium">{option.label}</span>
                        {formData.periodicity === option.value && (
                          <Check className="w-5 h-5 text-primary ml-auto" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="startDate" className="text-base font-semibold mb-4 block">
                  Fecha de Inicio
                </Label>
                <Input
                  id="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, startDate: e.target.value })}
                  min={new Date().toISOString().split("T")[0]}
                  className="w-full"
                />
              </div>
              <div>
                <Label htmlFor="startTime" className="text-base font-semibold mb-4 block">
                  Hora de Inicio
                </Label>
                <Input
                  id="startTime"
                  type="time"
                  value={formData.startTime}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, startTime: e.target.value })}
                  className="w-full"
                />
              </div>
              <div>
                <Label htmlFor="endDate" className="text-base font-semibold mb-4 block">
                  Fecha de Fin (Opcional)
                </Label>
                <Input
                  id="endDate"
                  type="date"
                  value={formData.endDate || ""}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setFormData({ ...formData, endDate: e.target.value || null })
                  }
                  min={formData.startDate}
                  className="w-full"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  Deja vacío si el recordatorio no tiene fecha de fin
                </p>
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-4">
              <div className="text-base font-semibold mb-4">Resumen del Recordatorio</div>
              <div className="space-y-4 p-4 border border-border rounded-lg bg-muted/30">
                <div className="flex items-center gap-3">
                  <Pill className="w-5 h-5 text-primary" />
                  <div>
                    <div className="text-sm text-muted-foreground">Medicina</div>
                    <div className="font-semibold">{selectedMedicine?.name || "No seleccionada"}</div>
                    {selectedMedicine?.dosage && (
                      <div className="text-sm text-muted-foreground">{selectedMedicine.dosage}</div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-primary" />
                  <div>
                    <div className="text-sm text-muted-foreground">Frecuencia</div>
                    <div className="font-semibold">
                      {formData.periodicity
                        ? formatPeriodicity(formData.periodicity)
                        : "No seleccionada"}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-primary" />
                  <div>
                    <div className="text-sm text-muted-foreground">Fecha y Hora de Inicio</div>
                    <div className="font-semibold">
                      {formData.startDate &&
                        formData.startTime &&
                        new Date(`${formData.startDate}T${formData.startTime}`).toLocaleString("es-ES", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                    </div>
                  </div>
                </div>
                {formData.endDate && (
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-primary" />
                    <div>
                      <div className="text-sm text-muted-foreground">Fecha de Fin</div>
                      <div className="font-semibold">
                        {new Date(formData.endDate).toLocaleDateString("es-ES", {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer with navigation */}
        <DialogFooter className="flex border-t border-border px-6 py-4 flex-shrink-0" style={{ display: 'flex', justifyContent: 'center' }}>
          <Button variant="outline" onClick={currentStep === 1 ? onClose : handlePrevious}>
            <ChevronLeft className="w-4 h-4 mr-2" />
            {currentStep === 1 ? "Cancelar" : "Anterior"}
          </Button>
          <div className="flex gap-2">
            {currentStep < 4 ? (
              <Button onClick={handleNext} disabled={!canProceed()}>
                Siguiente
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} className="bg-primary hover:bg-primary/90">
                Crear Recordatorio
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

