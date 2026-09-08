import React from 'react'

export default function ShootPlan({ shootOrder, logistics }) {
  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Optimized Shoot Order</h3>
        <p className="text-gray-500 text-sm mt-0.5">Nearest-neighbor route for minimum travel</p>
      </div>
      <div className="p-5">
        <div className="space-y-3">
          {shootOrder.map((item, idx) => (
            <div key={item.scene_number}>
              <div className="flex items-center gap-4 p-4 bg-gray-800/40 rounded-lg border border-gray-700/50">
                <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center text-white font-bold shrink-0">
                  {item.order}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium">{item.location.name}</p>
                  <p className="text-gray-400 text-sm truncate">{item.location.address}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-gray-300 text-sm">Scene {item.scene_number}</p>
                  <p className="text-emerald-400 text-xs font-medium">
                    {(item.location.total_score * 100).toFixed(0)}% match
                  </p>
                </div>
              </div>
              {item.travel_to_next && (
                <div className="flex items-center gap-3 ml-5 py-2 text-gray-500 text-sm">
                  <div className="w-px h-6 bg-gray-700" />
                  <span>→</span>
                  <span>
                    {item.travel_to_next.distance_km} km ·{' '}
                    {item.travel_to_next.duration_minutes.toFixed(0)} min drive
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wider">Total Distance</p>
              <p className="text-white text-lg font-bold mt-1">{logistics.total_distance_km} km</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wider">Travel Time</p>
              <p className="text-white text-lg font-bold mt-1">{logistics.total_travel_hours}h</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs uppercase tracking-wider">Est. Cost</p>
              <p className="text-amber-400 text-lg font-bold mt-1">
                {logistics.currency} {logistics.estimated_cost.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
