import { Fragment } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { SlotPerformanceData } from '@/api/dashboard'

interface SlotMapProps {
  slots: SlotPerformanceData[]
  device: string
  rows?: number
  cols?: number
  className?: string
}

function interpolateColor(ratio: number): string {
  const r = Math.round(28 + (255 - 28) * ratio)
  const g = Math.round(28 + (166 - 28) * ratio)
  const b = Math.round(41 + (0 - 41) * ratio)
  return `rgb(${r}, ${g}, ${b})`
}

function SlotMap({ slots, device, rows = 6, cols = 8, className }: SlotMapProps) {
  const deviceSlots = slots.filter(s => s.device === device)
  const maxRevenue = Math.max(...deviceSlots.map(s => s.revenue), 1)

  const rowLabels = Array.from({ length: rows }, (_, i) => String.fromCharCode(65 + i))
  const colLabels = Array.from({ length: cols }, (_, i) => String(i + 1).padStart(2, '0'))

  const slotMap = new Map(deviceSlots.map(s => [s.slot_code, s]))

  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Slot Map</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          data-testid="slot-grid"
          className="grid gap-1"
          style={{ gridTemplateColumns: `auto repeat(${cols}, 1fr)` }}
        >
          <div />
          {colLabels.map(col => (
            <div key={col} className="text-center text-xs text-gray-500">{col}</div>
          ))}

          {rowLabels.map(row => (
            <Fragment key={row}>
              <div className="flex items-center text-xs text-gray-500 pr-1">
                {row}
              </div>
              {colLabels.map(col => {
                const code = `0${row}${col}`
                const slot = slotMap.get(code)
                const ratio = slot ? slot.revenue / maxRevenue : 0

                return (
                  <div
                    key={`${row}-${col}`}
                    className="flex flex-col items-center justify-center rounded p-1 text-center"
                    style={{
                      backgroundColor: slot ? interpolateColor(ratio) : 'rgba(255,255,255,0.02)',
                      minHeight: 48,
                    }}
                  >
                    {slot ? (
                      <>
                        <span className="text-[10px] font-mono text-white/80">{slot.slot_code}</span>
                        <span className="text-[10px] font-medium text-white">${slot.revenue.toFixed(2)}</span>
                      </>
                    ) : (
                      <span className="text-[10px] text-gray-600">—</span>
                    )}
                  </div>
                )
              })}
            </Fragment>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default SlotMap
