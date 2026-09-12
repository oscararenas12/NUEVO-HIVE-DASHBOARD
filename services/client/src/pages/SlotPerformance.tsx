import { useState, useEffect } from 'react'
import { getSlots } from '@/api/dashboard'
import type { SlotsResponse } from '@/api/dashboard'
import SlotMap from '@/components/SlotMap'
import SlotRankings from '@/components/SlotRankings'
import PaymentTypes from '@/components/PaymentTypes'

const DEVICES = ['VK200044724', 'VK200044729']

function SlotPerformance() {
  const [data, setData] = useState<SlotsResponse | null>(null)
  const [selectedDevice, setSelectedDevice] = useState(DEVICES[0])

  useEffect(() => {
    getSlots().then(setData)
  }, [])

  if (!data) return null

  const filteredSlots = data.slots.filter(s => s.device === selectedDevice)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Slot Performance</h1>
        <p className="mt-1 text-sm text-gray-500">Revenue and activity by slot position</p>
      </div>

      <div className="flex gap-2">
        {DEVICES.map(device => (
          <button
            key={device}
            onClick={() => setSelectedDevice(device)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              selectedDevice === device
                ? 'bg-accent text-white'
                : 'bg-bg-surface text-gray-400 hover:bg-bg-surface-hover hover:text-white'
            }`}
          >
            {device}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <SlotMap slots={filteredSlots} device={selectedDevice} className="lg:col-span-3" />
        <SlotRankings slots={filteredSlots} className="lg:col-span-2" />
      </div>

      <PaymentTypes data={data.payment_types} />
    </div>
  )
}

export default SlotPerformance
