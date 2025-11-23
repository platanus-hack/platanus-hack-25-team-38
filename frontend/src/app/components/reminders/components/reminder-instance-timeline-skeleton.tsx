"use client"

import { Skeleton } from "@/components/ui/skeleton"

interface ReminderInstanceTimelineSkeletonProps {
  items?: number
}

export function ReminderInstanceTimelineSkeleton({ items = 5 }: ReminderInstanceTimelineSkeletonProps) {
  return (
    <div className="relative">
      {/* Horizontal timeline line */}
      <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
      
      <div className="relative flex items-start gap-3 overflow-x-auto pb-2 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        {Array.from({ length: items }).map((_, index) => (
          <div
            key={index}
            className="flex flex-col items-center gap-2 flex-shrink-0 min-w-[70px]"
          >
            {/* Status dot skeleton */}
            <div className="relative z-10">
              <Skeleton className="w-5 h-5 rounded-full border-2 border-background" />
            </div>
            
            {/* Time and status skeleton */}
            <div className="text-center px-2 py-1 rounded-md bg-muted/30 min-w-full space-y-1">
              <Skeleton className="h-3 w-10 mx-auto" />
              <Skeleton className="h-2.5 w-12 mx-auto" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

