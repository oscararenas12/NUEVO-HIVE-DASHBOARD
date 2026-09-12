import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { PaymentBreakdown } from '@/api/dashboard'

const CHART_COLORS = ['#ffa600', '#ff6b35', '#4ecdc4', '#45b7d1', '#96ceb4', '#c792ea']

interface PaymentTypesProps {
  data: PaymentBreakdown[]
  className?: string
}

function PaymentTypes({ data, className }: PaymentTypesProps) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Payment Methods</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center gap-6 lg:flex-row">
          <div className="w-full max-w-[240px]">
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={data}
                  dataKey="revenue"
                  nameKey="payment_type"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                >
                  {data.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1c1c29',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: 8,
                    color: '#d1d5db',
                  }}
                  formatter={(value: number) => `$${value.toFixed(2)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-2">
            {data.map((item, i) => (
              <div key={item.payment_type} className="flex items-center gap-3">
                <div
                  className="size-3 shrink-0 rounded-full"
                  style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }}
                />
                <span className="flex-1 text-sm text-gray-300">{item.payment_type}</span>
                <span className="text-sm font-medium text-white">${item.revenue.toFixed(2)}</span>
                <span className="w-12 text-right text-xs text-gray-400">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default PaymentTypes
