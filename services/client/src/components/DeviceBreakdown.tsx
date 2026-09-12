import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { DeviceStats } from '@/api/dashboard'

interface DeviceBreakdownProps {
  devices: DeviceStats[]
  className?: string
}

function DeviceBreakdown({ devices, className }: DeviceBreakdownProps) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Devices</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {devices.map((device) => (
          <div key={device.serial_num} className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white">{device.serial_num}</p>
                <p className="text-xs text-gray-500">{device.location}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-white">
                  ${device.revenue.toFixed(2)}
                </p>
                <p className="text-xs text-gray-500">{device.vends} vends</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-1.5 flex-1 rounded-full bg-white/5">
                <div
                  className="h-1.5 rounded-full bg-accent"
                  style={{ width: `${device.revenue_share}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">{device.revenue_share}%</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default DeviceBreakdown
