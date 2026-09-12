import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { WeeklyTrend, MonthlyTrend, HourlyPattern, DayOfWeekPattern } from '@/api/dashboard'

const AXIS_STYLE = { fill: '#9ca3af', fontSize: 12 }
const GRID_STROKE = 'rgba(255,255,255,0.06)'
const TOOLTIP_STYLE = {
  backgroundColor: '#1c1c29',
  border: '1px solid rgba(255,255,255,0.06)',
  borderRadius: 8,
  color: '#d1d5db',
}

function WeeklyRevenueChart({ data, className }: { data: WeeklyTrend[]; className?: string }) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Weekly Revenue</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="week_start" tick={AXIS_STYLE} tickFormatter={(d: string) => d.slice(5)} axisLine={{ stroke: GRID_STROKE }} />
            <YAxis tick={AXIS_STYLE} tickFormatter={(v: number) => `$${v}`} axisLine={{ stroke: GRID_STROKE }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => [`$${v.toFixed(2)}`, 'Revenue']} />
            <Line type="monotone" dataKey="revenue" stroke="#ffa600" strokeWidth={2} dot={{ fill: '#ffa600', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function MonthlyRevenueChart({ data, className }: { data: MonthlyTrend[]; className?: string }) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Monthly Revenue</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="month" tick={AXIS_STYLE} axisLine={{ stroke: GRID_STROKE }} />
            <YAxis tick={AXIS_STYLE} tickFormatter={(v: number) => `$${v}`} axisLine={{ stroke: GRID_STROKE }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => [`$${v.toFixed(2)}`, 'Revenue']} />
            <Bar dataKey="revenue" fill="#ffa600" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function HourlyPatternChart({ data, className }: { data: HourlyPattern[]; className?: string }) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Hourly Pattern</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="hour" tick={AXIS_STYLE} tickFormatter={(h: number) => `${h}:00`} axisLine={{ stroke: GRID_STROKE }} />
            <YAxis tick={AXIS_STYLE} axisLine={{ stroke: GRID_STROKE }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => [v.toFixed(1), 'Avg Vends']} labelFormatter={(h: number) => `${h}:00`} />
            <Bar dataKey="avg_vends" fill="#4ecdc4" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

function DayOfWeekChart({ data, className }: { data: DayOfWeekPattern[]; className?: string }) {
  return (
    <Card className={`border-border-subtle bg-bg-surface ${className ?? ''}`}>
      <CardHeader>
        <CardTitle className="text-white">Day of Week</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
            <XAxis dataKey="day_name" tick={AXIS_STYLE} tickFormatter={(d: string) => d.slice(0, 3)} axisLine={{ stroke: GRID_STROKE }} />
            <YAxis tick={AXIS_STYLE} axisLine={{ stroke: GRID_STROKE }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(v: number) => [v.toFixed(1), 'Avg Vends']} />
            <Bar dataKey="avg_vends" fill="#45b7d1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export { WeeklyRevenueChart, MonthlyRevenueChart, HourlyPatternChart, DayOfWeekChart }
