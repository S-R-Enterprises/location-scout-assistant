import React from 'react'

export default function SummaryCards({ report }) {
  const cards = [
    { label: 'Scenes Detected', value: report.total_scenes, color: 'text-emerald-400' },
    { label: 'Candidate Locations', value: report.total_locations, color: 'text-blue-400' },
    {
      label: 'Total Travel',
      value: `${report.logistics.total_travel_hours}h`,
      sub: `${report.logistics.total_distance_km} km`,
      color: 'text-amber-400',
    },
    {
      label: 'Estimated Cost',
      value: `${report.logistics.currency} ${report.logistics.estimated_cost.toLocaleString()}`,
      color: 'text-purple-400',
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-gray-900/60 border border-gray-800 rounded-xl p-5"
        >
          <p className="text-gray-500 text-sm mb-1">{card.label}</p>
          <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
          {card.sub && <p className="text-gray-500 text-xs mt-0.5">{card.sub}</p>}
        </div>
      ))}
    </div>
  )
}
