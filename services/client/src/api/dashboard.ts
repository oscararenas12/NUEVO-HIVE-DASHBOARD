const API_BASE = import.meta.env.VITE_API_URL ?? ''

// --- Interfaces ---

export interface OverviewStats {
  total_revenue: number
  total_vends: number
  avg_price: number
  active_devices: number
  revenue_change: number
  vends_change: number
  avg_price_change: number
  devices_change: number
}

export interface DailyRevenue {
  date: string
  revenue: number
  vends: number
}

export interface Transaction {
  item_ref: string
  device: string
  item_date: string
  amount: number
  slot_code: string
  payment_type: string
  settle_status: string
}

export interface OverviewResponse {
  stats: OverviewStats
  daily_revenue: DailyRevenue[]
  recent_transactions: Transaction[]
}

export interface DeviceStats {
  serial_num: string
  location: string
  revenue: number
  vends: number
  avg_price: number
  top_slot: string
  revenue_share: number
}

export interface DevicesResponse {
  devices: DeviceStats[]
}

export interface SlotPerformanceData {
  slot_code: string
  device: string
  revenue: number
  vends: number
  avg_price: number
  last_vend: string
}

export interface PaymentBreakdown {
  payment_type: string
  revenue: number
  vends: number
  percentage: number
}

export interface SlotsResponse {
  slots: SlotPerformanceData[]
  payment_types: PaymentBreakdown[]
}

export interface WeeklyTrend {
  week_start: string
  revenue: number
  vends: number
}

export interface MonthlyTrend {
  month: string
  revenue: number
  vends: number
}

export interface HourlyPattern {
  hour: number
  avg_vends: number
  avg_revenue: number
}

export interface DayOfWeekPattern {
  day: number
  day_name: string
  avg_vends: number
  avg_revenue: number
}

export interface TrendsResponse {
  weekly: WeeklyTrend[]
  monthly: MonthlyTrend[]
  hourly: HourlyPattern[]
  day_of_week: DayOfWeekPattern[]
}

// --- Mock Data ---

function generateDailyRevenue(): DailyRevenue[] {
  const days: DailyRevenue[] = []
  const base = new Date('2026-08-13')
  for (let i = 0; i < 30; i++) {
    const d = new Date(base)
    d.setDate(base.getDate() + i)
    const revenue = Math.round((18 + Math.random() * 30) * 100) / 100
    const vends = Math.round(revenue / 2.6)
    days.push({
      date: d.toISOString().slice(0, 10),
      revenue,
      vends,
    })
  }
  return days
}

const MOCK_DAILY_REVENUE = generateDailyRevenue()

const MOCK_TRANSACTIONS: Transaction[] = [
  { item_ref: '22248127354', device: 'VK200044724', item_date: '2026-09-11T16:19:45', amount: 2.50, slot_code: '0B06', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
  { item_ref: '22248127355', device: 'VK200044724', item_date: '2026-09-11T15:42:10', amount: 3.00, slot_code: '0D07', payment_type: 'Credit (Apple Pay EMV)', settle_status: 'SETTLED' },
  { item_ref: '22248127356', device: 'VK200044729', item_date: '2026-09-11T14:55:33', amount: 2.00, slot_code: '0A02', payment_type: 'Cash', settle_status: 'SETTLED' },
  { item_ref: '22248127357', device: 'VK200044724', item_date: '2026-09-11T13:30:21', amount: 2.50, slot_code: '0E03', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
  { item_ref: '22248127358', device: 'VK200044729', item_date: '2026-09-11T12:15:47', amount: 2.50, slot_code: '0C05', payment_type: 'Credit (Google Pay EMV)', settle_status: 'SETTLED' },
  { item_ref: '22248127359', device: 'VK200044724', item_date: '2026-09-11T11:08:19', amount: 3.00, slot_code: '0A06', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
  { item_ref: '22248127360', device: 'VK200044729', item_date: '2026-09-11T10:22:55', amount: 2.00, slot_code: '0B03', payment_type: 'Cash', settle_status: 'SETTLED' },
  { item_ref: '22248127361', device: 'VK200044724', item_date: '2026-09-11T09:45:12', amount: 2.50, slot_code: '0D04', payment_type: 'Credit (Apple Pay Cash EMV)', settle_status: 'SETTLED' },
  { item_ref: '22248127362', device: 'VK200044729', item_date: '2026-09-11T08:33:41', amount: 2.50, slot_code: '0E06', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
  { item_ref: '22248127363', device: 'VK200044724', item_date: '2026-09-10T17:20:08', amount: 3.00, slot_code: '0C02', payment_type: 'Credit (EMV Contactless)', settle_status: 'SETTLED' },
]

const MOCK_OVERVIEW: OverviewResponse = {
  stats: {
    total_revenue: 847.50,
    total_vends: 312,
    avg_price: 2.72,
    active_devices: 2,
    revenue_change: 12.5,
    vends_change: 8.3,
    avg_price_change: -1.2,
    devices_change: 0,
  },
  daily_revenue: MOCK_DAILY_REVENUE,
  recent_transactions: MOCK_TRANSACTIONS,
}

const MOCK_DEVICES: DevicesResponse = {
  devices: [
    { serial_num: 'VK200044724', location: 'South Gate, CA 90280', revenue: 523.50, vends: 195, avg_price: 2.68, top_slot: '0B06', revenue_share: 61.8 },
    { serial_num: 'VK200044729', location: 'South Gate, CA 90280', revenue: 324.00, vends: 117, avg_price: 2.77, top_slot: '0A02', revenue_share: 38.2 },
  ],
}

const MOCK_SLOTS: SlotsResponse = {
  slots: [
    { slot_code: '0A02', device: 'VK200044724', revenue: 85.00, vends: 34, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
    { slot_code: '0A06', device: 'VK200044724', revenue: 72.00, vends: 24, avg_price: 3.00, last_vend: '2026-09-11T11:08:19' },
    { slot_code: '0B03', device: 'VK200044724', revenue: 45.00, vends: 18, avg_price: 2.50, last_vend: '2026-09-10T14:22:55' },
    { slot_code: '0B06', device: 'VK200044724', revenue: 95.00, vends: 38, avg_price: 2.50, last_vend: '2026-09-11T16:19:45' },
    { slot_code: '0C02', device: 'VK200044724', revenue: 60.00, vends: 20, avg_price: 3.00, last_vend: '2026-09-10T17:20:08' },
    { slot_code: '0C05', device: 'VK200044724', revenue: 52.50, vends: 21, avg_price: 2.50, last_vend: '2026-09-09T15:33:12' },
    { slot_code: '0D04', device: 'VK200044724', revenue: 37.50, vends: 15, avg_price: 2.50, last_vend: '2026-09-11T09:45:12' },
    { slot_code: '0D07', device: 'VK200044724', revenue: 66.00, vends: 22, avg_price: 3.00, last_vend: '2026-09-11T15:42:10' },
    { slot_code: '0E03', device: 'VK200044724', revenue: 42.50, vends: 17, avg_price: 2.50, last_vend: '2026-09-11T13:30:21' },
    { slot_code: '0E06', device: 'VK200044724', revenue: 28.00, vends: 14, avg_price: 2.00, last_vend: '2026-09-08T10:15:33' },
    { slot_code: '0A02', device: 'VK200044729', revenue: 78.00, vends: 31, avg_price: 2.52, last_vend: '2026-09-11T14:55:33' },
    { slot_code: '0A06', device: 'VK200044729', revenue: 54.00, vends: 18, avg_price: 3.00, last_vend: '2026-09-10T12:08:19' },
    { slot_code: '0B03', device: 'VK200044729', revenue: 40.00, vends: 16, avg_price: 2.50, last_vend: '2026-09-11T10:22:55' },
    { slot_code: '0B06', device: 'VK200044729', revenue: 62.50, vends: 25, avg_price: 2.50, last_vend: '2026-09-11T09:30:45' },
    { slot_code: '0C05', device: 'VK200044729', revenue: 35.00, vends: 14, avg_price: 2.50, last_vend: '2026-09-11T12:15:47' },
    { slot_code: '0D04', device: 'VK200044729', revenue: 22.00, vends: 11, avg_price: 2.00, last_vend: '2026-09-09T08:45:12' },
    { slot_code: '0E06', device: 'VK200044729', revenue: 32.50, vends: 13, avg_price: 2.50, last_vend: '2026-09-11T08:33:41' },
  ],
  payment_types: [
    { payment_type: 'Credit (EMV Contactless)', revenue: 412.50, vends: 152, percentage: 48.7 },
    { payment_type: 'Cash', revenue: 148.00, vends: 58, percentage: 17.5 },
    { payment_type: 'Credit (Apple Pay EMV)', revenue: 126.00, vends: 46, percentage: 14.9 },
    { payment_type: 'Credit (Google Pay EMV)', revenue: 82.50, vends: 30, percentage: 9.7 },
    { payment_type: 'Credit', revenue: 48.00, vends: 16, percentage: 5.7 },
    { payment_type: 'Credit (Apple Pay Cash EMV)', revenue: 30.50, vends: 10, percentage: 3.6 },
  ],
}

const MOCK_TRENDS: TrendsResponse = {
  weekly: [
    { week_start: '2026-07-20', revenue: 185.50, vends: 68 },
    { week_start: '2026-07-27', revenue: 198.00, vends: 73 },
    { week_start: '2026-08-03', revenue: 210.50, vends: 78 },
    { week_start: '2026-08-10', revenue: 195.00, vends: 72 },
    { week_start: '2026-08-17', revenue: 222.00, vends: 82 },
    { week_start: '2026-08-24', revenue: 215.50, vends: 80 },
    { week_start: '2026-08-31', revenue: 230.00, vends: 85 },
    { week_start: '2026-09-07', revenue: 218.50, vends: 81 },
  ],
  monthly: [
    { month: '2026-05', revenue: 725.00, vends: 268 },
    { month: '2026-06', revenue: 780.50, vends: 289 },
    { month: '2026-07', revenue: 812.00, vends: 301 },
    { month: '2026-08', revenue: 847.50, vends: 312 },
  ],
  hourly: Array.from({ length: 24 }, (_, hour) => {
    const peak = hour >= 10 && hour <= 14
    const moderate = (hour >= 7 && hour < 10) || (hour > 14 && hour <= 18)
    return {
      hour,
      avg_vends: peak ? 2.8 + Math.random() * 1.2 : moderate ? 1.2 + Math.random() * 0.8 : Math.random() * 0.4,
      avg_revenue: peak ? 7.20 + Math.random() * 3 : moderate ? 3.10 + Math.random() * 2 : Math.random() * 1,
    }
  }).map(h => ({
    ...h,
    avg_vends: Math.round(h.avg_vends * 10) / 10,
    avg_revenue: Math.round(h.avg_revenue * 100) / 100,
  })),
  day_of_week: [
    { day: 0, day_name: 'Sunday', avg_vends: 8.2, avg_revenue: 21.30 },
    { day: 1, day_name: 'Monday', avg_vends: 12.5, avg_revenue: 32.50 },
    { day: 2, day_name: 'Tuesday', avg_vends: 13.1, avg_revenue: 34.10 },
    { day: 3, day_name: 'Wednesday', avg_vends: 14.0, avg_revenue: 36.40 },
    { day: 4, day_name: 'Thursday', avg_vends: 13.8, avg_revenue: 35.90 },
    { day: 5, day_name: 'Friday', avg_vends: 15.2, avg_revenue: 39.50 },
    { day: 6, day_name: 'Saturday', avg_vends: 10.5, avg_revenue: 27.30 },
  ],
}

// --- API Functions ---

async function handleResponse<T>(res: Response, fallback: string): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: fallback }))
    throw new Error(err.detail ?? fallback)
  }
  return res.json()
}

export async function getOverview(): Promise<OverviewResponse> {
  if (!API_BASE) return MOCK_OVERVIEW
  const res = await fetch(`${API_BASE}/dashboard/overview`, { credentials: 'include' })
  return handleResponse(res, 'Failed to load overview')
}

export async function getDevices(): Promise<DevicesResponse> {
  if (!API_BASE) return MOCK_DEVICES
  const res = await fetch(`${API_BASE}/dashboard/devices`, { credentials: 'include' })
  return handleResponse(res, 'Failed to load devices')
}

export async function getSlots(): Promise<SlotsResponse> {
  if (!API_BASE) return MOCK_SLOTS
  const res = await fetch(`${API_BASE}/dashboard/slots`, { credentials: 'include' })
  return handleResponse(res, 'Failed to load slots')
}

export async function getTrends(): Promise<TrendsResponse> {
  if (!API_BASE) return MOCK_TRENDS
  const res = await fetch(`${API_BASE}/dashboard/trends`, { credentials: 'include' })
  return handleResponse(res, 'Failed to load trends')
}
