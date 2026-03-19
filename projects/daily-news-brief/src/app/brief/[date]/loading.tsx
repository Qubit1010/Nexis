export default function BriefLoading() {
  return (
    <div className="max-w-4xl mx-auto px-8 py-10 animate-pulse">
      {/* Header skeleton */}
      <div className="rounded-xl border border-border/50 p-6 sm:p-8">
        <div className="h-3 w-32 bg-muted/40 rounded mb-4" />
        <div className="h-8 w-72 bg-muted/40 rounded mb-4" />
        <div className="flex gap-2">
          <div className="h-7 w-24 bg-muted/30 rounded-full" />
          <div className="h-7 w-24 bg-muted/30 rounded-full" />
          <div className="h-7 w-20 bg-muted/30 rounded-full" />
        </div>
      </div>

      {/* Sentiment skeleton */}
      <div className="mt-8 rounded-xl border border-border/50 p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-muted/40" />
          <div className="space-y-2">
            <div className="h-3 w-28 bg-muted/30 rounded" />
            <div className="h-5 w-20 bg-muted/40 rounded-full" />
          </div>
        </div>
        <div className="space-y-2">
          <div className="h-3 w-full bg-muted/30 rounded" />
          <div className="h-3 w-4/5 bg-muted/30 rounded" />
        </div>
        <div className="mt-5 pl-4 border-l-2 border-muted/30">
          <div className="h-3 w-40 bg-muted/30 rounded mb-2" />
          <div className="h-4 w-full bg-muted/40 rounded" />
        </div>
      </div>

      {/* Trending skeleton */}
      <div className="mt-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-muted/40" />
          <div className="space-y-2">
            <div className="h-5 w-32 bg-muted/40 rounded" />
            <div className="h-3 w-48 bg-muted/30 rounded" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-xl border border-border/40 p-5">
              <div className="h-6 w-20 bg-muted/30 rounded-lg mb-3" />
              <div className="h-4 w-3/4 bg-muted/40 rounded mb-2" />
              <div className="space-y-1.5">
                <div className="h-3 w-full bg-muted/30 rounded" />
                <div className="h-3 w-5/6 bg-muted/30 rounded" />
              </div>
              <div className="h-1.5 w-full bg-muted/20 rounded-full mt-3" />
              <div className="flex gap-1.5 mt-3">
                <div className="h-5 w-14 bg-muted/20 rounded-full" />
                <div className="h-5 w-16 bg-muted/20 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content ideas skeleton */}
      <div className="mt-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-muted/40" />
          <div className="space-y-2">
            <div className="h-5 w-44 bg-muted/40 rounded" />
            <div className="h-3 w-56 bg-muted/30 rounded" />
          </div>
        </div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="rounded-xl border border-border/40 p-5 mb-3">
            <div className="flex gap-2 mb-3">
              <div className="h-5 w-16 bg-muted/30 rounded-full" />
              <div className="h-5 w-20 bg-muted/30 rounded-full" />
            </div>
            <div className="h-4 w-2/3 bg-muted/40 rounded mb-2" />
            <div className="h-3 w-full bg-muted/30 rounded" />
            <div className="mt-3 p-3 rounded-lg bg-muted/10">
              <div className="h-3 w-12 bg-muted/30 rounded mb-2" />
              <div className="h-3 w-full bg-muted/20 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
