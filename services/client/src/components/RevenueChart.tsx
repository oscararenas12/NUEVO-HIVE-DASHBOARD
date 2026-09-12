import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { DailyRevenue } from '@/api/dashboard'

interface RevenueChartProps {
  data: DailyRevenue[]
  className?: string
}

function RevenueChart({ data, className }: RevenueChartProps) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Daily Revenue</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis
              dataKey="date"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(d: string) => d.slice(5)}
              axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
            />
            <YAxis
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(v: number) => `$${v}`}
              axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1c1c29',
                border: '1px solid rgba(255,255,255,0.06)',
                borderRadius: 8,
                color: '#d1d5db',
              }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Revenue']}
              labelFormatter={(label: string) => label}
            />
            <Bar dataKey="revenue" fill="#ffa600" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export default RevenueChart
