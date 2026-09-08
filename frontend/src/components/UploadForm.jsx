import React, { useState, useRef } from 'react'
import { analyzeScreenplay } from '../services/api'

const SAMPLE_TEXT = `INT. OFFICE BUILDING - DAY

JAKE sits at his desk, staring at the computer screen. Papers are scattered everywhere.

EXT. BUSY STREET MARKET - DAY

MIRA navigates through the crowded marketplace, dodging vendors and shoppers. The sounds of haggling fill the air.

INT. COFFEE SHOP - NIGHT

Jake and Mira sit across from each other in a dimly lit corner booth. Rain streaks down the windows.

EXT. ABANDONED WAREHOUSE DISTRICT - NIGHT

Jake approaches the crumbling industrial buildings. Chain-link fences surround the property. Graffiti covers every surface.

EXT. RIVERBRIDGE - DUSK

Mira stands on the old stone bridge, watching the sunset over the river. The water reflects orange and pink.

INT. HOTEL ROOM - NIGHT

Jake paces the small room. A single lamp casts harsh shadows on the walls.

EXT. MOUNTAIN TRAIL - DAWN

Mira hikes along a narrow trail through dense forest. Mist hangs in the trees.

INT. POLICE STATION - DAY

Jake reviews documents at a metal desk. Fluorescent lights buzz overhead.`

export default function UploadForm({ onSubmit, onResult, onError }) {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [baseRegion, setBaseRegion] = useState('Kathmandu Valley')
  const [projectName, setProjectName] = useState('Demo Project')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file && !text.trim()) {
      onError('Please upload a PDF or paste screenplay text.')
      return
    }
    onSubmit()
    try {
      const result = await analyzeScreenplay({
        file,
        text: text.trim() || undefined,
        baseRegion,
        projectName,
      })
      onResult(result)
    } catch (err) {
      onError(err.message)
    }
  }

  const loadSample = () => {
    setText(SAMPLE_TEXT)
    setProjectName('Riverside Mystery')
    setBaseRegion('Kathmandu Valley')
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-white mb-3">
          Script to Shoot Plan
        </h2>
        <p className="text-gray-400 text-lg">
          Upload a screenplay and get AI-powered location scouting with optimized shoot schedules.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="My Film Project"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1.5">Base Region</label>
            <input
              type="text"
              value={baseRegion}
              onChange={(e) => setBaseRegion(e.target.value)}
              className="w-full px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="Kathmandu Valley"
            />
          </div>
        </div>

        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
            dragOver
              ? 'border-emerald-500 bg-emerald-500/5'
              : 'border-gray-700 hover:border-gray-600 bg-gray-900/30'
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragOver(false)
            const f = e.dataTransfer.files[0]
            if (f) setFile(f)
          }}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <div className="text-4xl mb-3 text-gray-600">📄</div>
          {file ? (
            <p className="text-emerald-400 font-medium">{file.name}</p>
          ) : (
            <>
              <p className="text-gray-300 font-medium">Drop screenplay PDF here or click to browse</p>
              <p className="text-gray-500 text-sm mt-1">PDF files supported</p>
            </>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1.5">
            Or paste screenplay text
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={8}
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white font-mono text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-y"
            placeholder={"INT. OFFICE - DAY\n\nJAKE sits at his desk..."}
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!file && !text.trim()}
            className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-lg transition-colors"
          >
            Analyze Screenplay
          </button>
          <button
            type="button"
            onClick={loadSample}
            className="px-6 py-3 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-lg transition-colors border border-gray-700"
          >
            Load Sample
          </button>
        </div>
      </form>
    </div>
  )
}
