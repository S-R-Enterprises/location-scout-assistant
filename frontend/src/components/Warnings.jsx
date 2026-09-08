import React from 'react'

export default function Warnings({ warnings }) {
  if (!warnings || warnings.length === 0) return null

  return (
    <div className="bg-amber-950/30 border border-amber-800/50 rounded-xl p-5">
      <h3 className="text-amber-400 font-semibold mb-2">⚠ Notes & Disclaimers</h3>
      <ul className="space-y-1.5">
        {warnings.map((w, i) => (
          <li key={i} className="text-amber-200/70 text-sm flex gap-2">
            <span className="text-amber-600">•</span>
            {w}
          </li>
        ))}
      </ul>
    </div>
  )
}
