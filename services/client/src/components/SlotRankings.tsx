import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { SlotPerformanceData } from '@/api/dashboard'

interface SlotRankingsProps {
  slots: SlotPerformanceData[]
  className?: string
}

function SlotRankings({ slots, className }: SlotRankingsProps) {
  const sorted = [...slots].sort((a, b) => b.revenue - a.revenue)
  const top = sorted.slice(0, 5)
  const bottom = sorted.slice(-5).reverse()
  const maxRevenue = sorted[0]?.revenue ?? 1

  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Slot Rankings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <h3 className="mb-3 text-sm font-medium text-positive">Top Performers</h3>
          <div className="space-y-2">
            {top.map((slot, i) => (
              <div key={slot.slot_code} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 text-xs text-gray-500">{i + 1}.</span>
                    <span className="font-mono text-sm text-accent">{slot.slot_code}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{slot.vends} vends</span>
                    <span className="text-sm font-medium text-white">${slot.revenue.toFixed(2)}</span>
                  </div>
                </div>
                <div className="ml-7 h-1 rounded-full bg-white/5">
                  <div
                    className="h-1 rounded-full bg-positive/50"
                    style={{ width: `${(slot.revenue / maxRevenue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-medium text-negative">Lowest Performers</h3>
          <div className="space-y-2">
            {bottom.map((slot, i) => (
              <div key={slot.slot_code} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 text-xs text-gray-500">{sorted.length - 4 + i}.</span>
                    <span className="font-mono text-sm text-accent">{slot.slot_code}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">{slot.vends} vends</span>
                    <span className="text-sm font-medium text-white">${slot.revenue.toFixed(2)}</span>
                  </div>
                </div>
                <div className="ml-7 h-1 rounded-full bg-white/5">
                  <div
                    className="h-1 rounded-full bg-negative/50"
                    style={{ width: `${(slot.revenue / maxRevenue) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default SlotRankings
