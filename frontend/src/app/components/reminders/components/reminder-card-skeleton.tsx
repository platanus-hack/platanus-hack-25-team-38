"use client"

import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export function ReminderCardSkeleton() {
  return (
    <Card className="p-6">
      <div className="flex gap-6">
        <div className="flex flex-col items-center gap-3">
          <Skeleton className="w-24 h-32 rounded-2xl" />
          <Skeleton className="w-16 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <Skeleton className="h-7 w-48 mb-2" />
              <Skeleton className="h-4 w-32" />
            </div>
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>

          <div className="flex gap-4 mb-4">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-28" />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Skeleton className="w-10 h-10 rounded" />
        </div>
      </div>
    </Card>
  )
}

