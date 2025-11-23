"use client"

import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export function TimelineItemSkeleton() {
  return (
    <div className="relative flex gap-6">
      {/* Timeline dot skeleton */}
      <Skeleton className="relative z-10 w-12 h-12 rounded-full border-4 border-background" />

      {/* Event Card skeleton */}
      <Card className="flex-1 p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>

            <Skeleton className="h-6 w-32 mb-2" />
            <Skeleton className="h-4 w-24 mb-2" />
            
            {/* Intentos skeleton */}
            <div className="flex items-center gap-1 mt-2">
              <Skeleton className="h-3 w-3 rounded" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>

          {/* Right side: buttons and pill icon */}
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-2">
              <Skeleton className="h-8 w-32 rounded-md" />
              <Skeleton className="h-9 w-9 rounded-md" />
            </div>
            <Skeleton className="w-8 h-8 rounded" />
          </div>
        </div>
      </Card>
    </div>
  )
}

