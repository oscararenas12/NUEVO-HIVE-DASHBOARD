import type { ReactNode } from 'react'

function createMockComponent(name: string) {
  return function MockComponent({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) {
    return <div data-testid={`mock-${name}`} {...filterProps(props)}>{children}</div>
  }
}

function filterProps(props: Record<string, unknown>) {
  const safe: Record<string, unknown> = {}
  for (const [key, val] of Object.entries(props)) {
    if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean') {
      safe[`data-${key.toLowerCase()}`] = String(val)
    }
  }
  return safe
}

export const ResponsiveContainer = createMockComponent('responsive-container')
export const BarChart = createMockComponent('bar-chart')
export const Bar = createMockComponent('bar')
export const AreaChart = createMockComponent('area-chart')
export const Area = createMockComponent('area')
export const LineChart = createMockComponent('line-chart')
export const Line = createMockComponent('line')
export const PieChart = createMockComponent('pie-chart')
export const Pie = createMockComponent('pie')
export const Cell = createMockComponent('cell')
export const XAxis = createMockComponent('x-axis')
export const YAxis = createMockComponent('y-axis')
export const CartesianGrid = createMockComponent('cartesian-grid')
export const Tooltip = createMockComponent('tooltip')
export const Legend = createMockComponent('legend')
