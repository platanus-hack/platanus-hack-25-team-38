"use client"

import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export function TimelineItemSkeleton() {
  return (
    <div className="relative flex gap-6">
      <Skeleton className="relative z-10 w-12 h-12 rounded-full border-4 border-background" />

      <Card className="flex-1 p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>

            <Skeleton className="h-6 w-32 mb-2" />
            <Skeleton className="h-4 w-24" />
          </div>

          <Skeleton className="w-8 h-8 rounded" />
        </div>
      </Card>
    </div>
  )
}

