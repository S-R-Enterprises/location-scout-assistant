import React from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import L from 'leaflet'

const createIcon = (color) =>
  L.divIcon({
    className: '',
    html: `<div style="width:24px;height:24px;background:${color};border:2px solid white;border-radius:50%;box-shadow:0 2px 4px rgba(0,0,0,0.3)"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  })

const orderIcon = createIcon('#10b981')
const candidateIcon = createIcon('#6366f1')

export default function MapView({ shootOrder, scenesLocations }) {
  const defaultCenter = [27.7172, 85.324]
  const positions = shootOrder.map((item) => [item.location.lat, item.location.lng])
  const center = positions.length > 0 ? positions[0] : defaultCenter

  const routePositions = shootOrder
    .filter((item) => item.travel_to_next)
    .map((item) => [
      [item.location.lat, item.location.lng],
      [item.travel_to_next.to_lat, item.travel_to_next.to_lng],
    ])

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Location Map</h3>
      </div>
      <div className="h-[400px]">
        <MapContainer
          center={center}
          zoom={12}
          style={{ height: '100%', width: '100%' }}
          className="bg-gray-900"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {shootOrder.map((item) => (
            <Marker
              key={item.scene_number}
              position={[item.location.lat, item.location.lng]}
              icon={orderIcon}
            >
              <Popup>
                <div className="text-sm">
                  <strong>{item.location.name}</strong>
                  <br />
                  Scene {item.scene_number} · {(item.location.total_score * 100).toFixed(0)}% match
                  <br />
                  <span className="text-gray-500">{item.location.address}</span>
                </div>
              </Popup>
            </Marker>
          ))}
          {scenesLocations.flatMap((sl) =>
            sl.candidates.slice(1).map((c, i) => (
              <Marker
                key={`${sl.scene.scene_number}-c${i}`}
                position={[c.lat, c.lng]}
                icon={candidateIcon}
              >
                <Popup>
                  <div className="text-sm">
                    <strong>{c.name}</strong>
                    <br />
                    Alternative for Scene {sl.scene.scene_number}
                    <br />
                    <span className="text-gray-500">{c.address}</span>
                  </div>
                </Popup>
              </Marker>
            ))
          )}
          {routePositions.map((pos, i) => (
            <Polyline
              key={i}
              positions={pos}
              color="#10b981"
              weight={2}
              opacity={0.6}
              dashArray="8 8"
            />
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
