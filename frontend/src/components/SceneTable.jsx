import React from 'react'

export default function SceneTable({ scenesLocations }) {
  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-white">Scene Breakdown</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400">
              <th className="text-left px-5 py-3 font-medium">Scene</th>
              <th className="text-left px-5 py-3 font-medium">Type</th>
              <th className="text-left px-5 py-3 font-medium">Location</th>
              <th className="text-left px-5 py-3 font-medium">Time</th>
              <th className="text-left px-5 py-3 font-medium">Best Match</th>
              <th className="text-left px-5 py-3 font-medium">Score</th>
              <th className="text-left px-5 py-3 font-medium">Candidates</th>
            </tr>
          </thead>
          <tbody>
            {scenesLocations.map((sl) => (
              <tr key={sl.scene.scene_number} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                <td className="px-5 py-3 text-white font-mono font-semibold">
                  {sl.scene.scene_number}
                </td>
                <td className="px-5 py-3">
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    sl.scene.int_ext === 'INT'
                      ? 'bg-blue-900/60 text-blue-300'
                      : sl.scene.int_ext === 'EXT'
                      ? 'bg-green-900/60 text-green-300'
                      : 'bg-purple-900/60 text-purple-300'
                  }`}>
                    {sl.scene.int_ext}
                  </span>
                </td>
                <td className="px-5 py-3 text-gray-300 max-w-[200px] truncate">
                  {sl.scene.location_description}
                </td>
                <td className="px-5 py-3 text-gray-400">{sl.scene.time_of_day}</td>
                <td className="px-5 py-3 text-white">
                  {sl.best_location ? sl.best_location.name : '—'}
                </td>
                <td className="px-5 py-3">
                  {sl.best_location ? (
                    <span className={`font-semibold ${
                      sl.best_location.total_score >= 0.7
                        ? 'text-emerald-400'
                        : sl.best_location.total_score >= 0.4
                        ? 'text-amber-400'
                        : 'text-red-400'
                    }`}>
                      {(sl.best_location.total_score * 100).toFixed(0)}%
                    </span>
                  ) : '—'}
                </td>
                <td className="px-5 py-3 text-gray-400">{sl.candidates.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
