import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('Dashboard API (fallback on error)', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.stubEnv('VITE_API_URL', '/api')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('Network error')),
    )
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it('getOverview falls back to mock on fetch error', async () => {
    const { getOverview } = await import('@/api/dashboard')
    const data = await getOverview()
    expect(data.stats.total_revenue).toBeGreaterThan(0)
    expect(data.daily_revenue.length).toBeGreaterThan(0)
  })

  it('getDevices falls back to mock on fetch error', async () => {
    const { getDevices } = await import('@/api/dashboard')
    const data = await getDevices()
    expect(data.devices.length).toBeGreaterThan(0)
  })

  it('getSlots falls back to mock on fetch error', async () => {
    const { getSlots } = await import('@/api/dashboard')
    const data = await getSlots()
    expect(data.slots.length).toBeGreaterThan(0)
    expect(data.payment_types.length).toBeGreaterThan(0)
  })

  it('getTrends falls back to mock on fetch error', async () => {
    const { getTrends } = await import('@/api/dashboard')
    const data = await getTrends()
    expect(data.weekly.length).toBeGreaterThan(0)
    expect(data.hourly).toHaveLength(24)
  })
})
