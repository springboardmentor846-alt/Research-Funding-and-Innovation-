import { cn } from "@/lib/utils";

// Single skeleton bar
export function Skeleton({ className }) {
  return (
    <div className={cn("animate-pulse rounded-md bg-slate-200", className)} />
  );
}

// Card skeleton used across pages
export function CardSkeleton() {
  return (
    <div className="rounded-xl border bg-white p-5 space-y-3 shadow-sm">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-3 w-2/3" />
      <Skeleton className="h-3 w-1/2" />
      <Skeleton className="h-8 w-24 mt-2" />
    </div>
  );
}

// Grid of card skeletons
export function CardGridSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

// Table row skeleton
export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton className="h-4 flex-1" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-20" />
        </div>
      ))}
    </div>
  );
}

// Chart skeleton
export function ChartSkeleton({ height = "h-64" }) {
  return <Skeleton className={cn("w-full rounded-xl", height)} />;
}
