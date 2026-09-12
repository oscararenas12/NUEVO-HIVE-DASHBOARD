import { describe, it, expect } from 'vitest'
import { getOverview, getDevices, getSlots, getTrends } from '@/api/dashboard'

describe('Dashboard API (mock data)', () => {
  describe('getOverview', () => {
    it('returns overview stats with expected fields', async () => {
      const data = await getOverview()
      expect(data.stats.total_revenue).toBeGreaterThan(0)
      expect(data.stats.total_vends).toBeGreaterThan(0)
      expect(data.stats.avg_price).toBeGreaterThan(0)
      expect(data.stats.active_devices).toBe(2)
      expect(typeof data.stats.revenue_change).toBe('number')
      expect(typeof data.stats.vends_change).toBe('number')
      expect(typeof data.stats.avg_price_change).toBe('number')
    })

    it('returns 30 days of daily revenue', async () => {
      const data = await getOverview()
      expect(data.daily_revenue).toHaveLength(30)
      expect(data.daily_revenue[0]).toHaveProperty('date')
      expect(data.daily_revenue[0]).toHaveProperty('revenue')
      expect(data.daily_revenue[0]).toHaveProperty('vends')
    })

    it('returns recent transactions with real slot codes', async () => {
      const data = await getOverview()
      expect(data.recent_transactions.length).toBeGreaterThan(0)
      const tx = data.recent_transactions[0]
      expect(tx.item_ref).toBeTruthy()
      expect(tx.device).toMatch(/^VK/)
      expect(tx.slot_code).toMatch(/^0[A-F]\d{2}$/)
      expect(tx.amount).toBeGreaterThan(0)
      expect(tx.settle_status).toBe('SETTLED')
    })
  })

  describe('getDevices', () => {
    it('returns two devices with expected serials', async () => {
      const data = await getDevices()
      expect(data.devices).toHaveLength(2)
      const serials = data.devices.map(d => d.serial_num)
      expect(serials).toContain('VK200044724')
      expect(serials).toContain('VK200044729')
    })

    it('device stats include revenue share summing to ~100%', async () => {
      const data = await getDevices()
      const totalShare = data.devices.reduce((sum, d) => sum + d.revenue_share, 0)
      expect(totalShare).toBeCloseTo(100, 0)
    })
  })

  describe('getSlots', () => {
    it('returns slots for both devices', async () => {
      const data = await getSlots()
      const devices = new Set(data.slots.map(s => s.device))
      expect(devices.size).toBe(2)
    })

    it('returns payment type breakdown summing to ~100%', async () => {
      const data = await getSlots()
      const totalPct = data.payment_types.reduce((sum, p) => sum + p.percentage, 0)
      expect(totalPct).toBeCloseTo(100, 0)
    })

    it('includes expected payment types', async () => {
      const data = await getSlots()
      const types = data.payment_types.map(p => p.payment_type)
      expect(types).toContain('Credit (EMV Contactless)')
      expect(types).toContain('Cash')
    })
  })

  describe('getTrends', () => {
    it('returns weekly trends', async () => {
      const data = await getTrends()
      expect(data.weekly.length).toBeGreaterThan(0)
      expect(data.weekly[0]).toHaveProperty('week_start')
      expect(data.weekly[0]).toHaveProperty('revenue')
    })

    it('returns monthly trends', async () => {
      const data = await getTrends()
      expect(data.monthly.length).toBeGreaterThan(0)
      expect(data.monthly[0].month).toMatch(/^\d{4}-\d{2}$/)
    })

    it('returns 24 hourly pattern entries', async () => {
      const data = await getTrends()
      expect(data.hourly).toHaveLength(24)
      expect(data.hourly[0].hour).toBe(0)
      expect(data.hourly[23].hour).toBe(23)
    })

    it('returns 7 day-of-week entries', async () => {
      const data = await getTrends()
      expect(data.day_of_week).toHaveLength(7)
      expect(data.day_of_week[0].day_name).toBe('Sunday')
      expect(data.day_of_week[5].day_name).toBe('Friday')
    })
  })
})
