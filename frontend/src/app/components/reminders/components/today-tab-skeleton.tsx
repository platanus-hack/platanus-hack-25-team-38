"use client"

import { Card } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { TimelineItemSkeleton } from "./timeline-item-skeleton"

export function TodayTabSkeleton() {
  return (
    <div className="flex-1 overflow-auto p-6">
      <Skeleton className="h-7 w-64 mb-6" />
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-6 items-start">
            {/* Avatar skeleton */}
            <div className="flex justify-start">
              <Skeleton className="w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 rounded-full" />
            </div>
            
            {/* Right column: Dashboard + Timeline items */}
            <div className="space-y-6">
              {/* Avatar Dashboard skeleton */}
              <Card className="w-full p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <Skeleton className="h-6 w-20 mb-2" />
                    <Skeleton className="h-3 w-12" />
                  </div>
                  <Skeleton className="h-9 w-40" />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center">
                    <Skeleton className="h-4 w-12 mx-auto mb-1" />
                    <Skeleton className="h-7 w-8 mx-auto" />
                  </div>
                  <div className="text-center">
                    <Skeleton className="h-4 w-16 mx-auto mb-1" />
                    <Skeleton className="h-7 w-8 mx-auto" />
                  </div>
                  <div className="text-center">
                    <Skeleton className="h-4 w-16 mx-auto mb-1" />
                    <Skeleton className="h-7 w-8 mx-auto" />
                  </div>
                </div>
              </Card>
              
              {/* Timeline items skeleton */}
              <div className="relative space-y-6">
                <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border"></div>
                {[1, 2, 3].map((i) => (
                  <TimelineItemSkeleton key={i} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

