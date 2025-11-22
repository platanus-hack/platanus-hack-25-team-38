"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import {
  TodayTab,
  ConfigTab,
  MedicineDetailModal,
  DeleteConfirmationModal,
  ActivateReminderModal,
  Reminder,
} from "./components"
import { RemindersService } from "@/lib/reminders"
import { api } from "@/lib/api"
import type { ReminderInstance } from "./components/types"

export function RemindersView() {
  const [activeTab, setActiveTab] = useState<"today" | "config">("today")
  const [searchQuery, setSearchQuery] = useState("")
  const [filterActive, setFilterActive] = useState<boolean | null>(null)
  const [selectedReminder, setSelectedReminder] = useState<Reminder | null>(null)
  const [showMedicineDetail, setShowMedicineDetail] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showActivateDialog, setShowActivateDialog] = useState(false)
  
  // Data state - separate loading for each tab
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [reminderInstances, setReminderInstances] = useState<ReminderInstance[]>([])
  const [loadingToday, setLoadingToday] = useState(false)
  const [loadingConfig, setLoadingConfig] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Track which tabs have been loaded
  const [loadedTabs, setLoadedTabs] = useState<Set<"today" | "config">>(new Set())
  
  // Action loading states
  const [togglingReminderId, setTogglingReminderId] = useState<number | null>(null)
  const [deletingReminderId, setDeletingReminderId] = useState<number | null>(null)
  const [activatingReminderId, setActivatingReminderId] = useState<number | null>(null)

  // Load data when tab changes
  useEffect(() => {
    if (!loadedTabs.has(activeTab)) {
      loadTabData(activeTab)
    }
  }, [activeTab, loadedTabs])

  const loadTabData = async (tab: "today" | "config") => {
    if (tab === "today") {
      setLoadingToday(true)
      setError(null)
      try {
        const instancesData = await RemindersService.getReminderInstancesWithMedicine()
        setReminderInstances(instancesData)
        setLoadedTabs((prev) => new Set(prev).add("today"))
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar datos")
        console.error("Error loading today data:", err)
      } finally {
        setLoadingToday(false)
      }
    } else if (tab === "config") {
      setLoadingConfig(true)
      setError(null)
      try {
        const remindersData = await RemindersService.getRemindersWithMedicine()
        setReminders(remindersData)
        setLoadedTabs((prev) => new Set(prev).add("config"))
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar datos")
        console.error("Error loading config data:", err)
      } finally {
        setLoadingConfig(false)
      }
    }
  }

  const handleToggleActive = async (reminder: Reminder) => {
    if (reminder.is_active) {
      // Deactivate immediately
      setTogglingReminderId(reminder.id)
      try {
        await api.patchReminder(reminder.id, { is_active: false })
        // Reload config tab data
        if (loadedTabs.has("config")) {
          await loadTabData("config")
        }
      } catch (err) {
        console.error("Error deactivating reminder:", err)
        alert("Error al desactivar el recordatorio")
      } finally {
        setTogglingReminderId(null)
      }
    } else {
      // Show dialog to reactivate
      setSelectedReminder(reminder)
      setShowActivateDialog(true)
    }
  }

  const handleDeleteReminder = async () => {
    if (!selectedReminder) return
    
    setDeletingReminderId(selectedReminder.id)
    try {
      await api.deleteReminder(selectedReminder.id)
      setShowDeleteDialog(false)
      setShowMedicineDetail(false)
      // Reload config tab data
      if (loadedTabs.has("config")) {
        await loadTabData("config")
      }
    } catch (err) {
      console.error("Error deleting reminder:", err)
      alert("Error al eliminar el recordatorio")
    } finally {
      setDeletingReminderId(null)
    }
  }

  const handleCardClick = (reminder: Reminder) => {
    setSelectedReminder(reminder)
    setShowMedicineDetail(true)
  }

  const handleShowDeleteDialog = () => {
    setShowDeleteDialog(true)
  }

  const handleActivateReminder = async () => {
    if (!selectedReminder) return
    
    setActivatingReminderId(selectedReminder.id)
    try {
      await api.patchReminder(selectedReminder.id, { is_active: true })
      setShowActivateDialog(false)
      // Reload config tab data
      if (loadedTabs.has("config")) {
        await loadTabData("config")
      }
    } catch (err) {
      console.error("Error activating reminder:", err)
      alert("Error al activar el recordatorio")
    } finally {
      setActivatingReminderId(null)
    }
  }
  
  const handleTabChange = (tab: "today" | "config") => {
    setActiveTab(tab)
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Recordatorios</h2>
            <p className="text-muted-foreground mt-1">Gestiona los recordatorios de medicinas</p>
          </div>
          <Button className="bg-primary hover:bg-primary/90">
            <Plus className="w-4 h-4 mr-2" />
            Nuevo
          </Button>
        </div>

        <div className="mt-6 flex gap-4">
          <button
            onClick={() => handleTabChange("today")}
            className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
              activeTab === "today" ? "text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Hoy
            {activeTab === "today" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
          <button
            onClick={() => handleTabChange("config")}
            className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
              activeTab === "config" ? "text-primary" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Configuración
            {activeTab === "config" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
        </div>
      </div>

      {error && (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-red-600">Error: {error}</p>
        </div>
      )}

      {!error && (
        <>
          {activeTab === "today" && (
            <TodayTab
              reminderInstances={reminderInstances.filter((instance) => {
                const instanceDate = new Date(instance.scheduled_datetime)
                const today = new Date()
                today.setHours(0, 0, 0, 0)
                const tomorrow = new Date(today)
                tomorrow.setDate(tomorrow.getDate() + 1)
                return instanceDate >= today && instanceDate < tomorrow
              })}
              loading={loadingToday}
            />
          )}

          {activeTab === "config" && (
            <ConfigTab
              reminders={reminders}
              searchQuery={searchQuery}
              filterActive={filterActive}
              onSearchChange={setSearchQuery}
              onFilterChange={setFilterActive}
              onCardClick={handleCardClick}
              onToggleActive={handleToggleActive}
              loading={loadingConfig}
              togglingReminderId={togglingReminderId}
            />
          )}
        </>
      )}

      <MedicineDetailModal
        isOpen={showMedicineDetail}
        onClose={() => setShowMedicineDetail(false)}
        reminder={selectedReminder}
        onDelete={handleShowDeleteDialog}
        onToggleActive={handleToggleActive}
        isToggling={togglingReminderId === selectedReminder?.id}
        isDeleting={deletingReminderId === selectedReminder?.id}
      />

      <DeleteConfirmationModal
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        reminder={selectedReminder}
        onConfirm={handleDeleteReminder}
        loading={deletingReminderId === selectedReminder?.id}
      />

      <ActivateReminderModal
        isOpen={showActivateDialog}
        onClose={() => setShowActivateDialog(false)}
        reminder={selectedReminder}
        onConfirm={handleActivateReminder}
        loading={activatingReminderId === selectedReminder?.id}
      />
    </div>
  )
}
