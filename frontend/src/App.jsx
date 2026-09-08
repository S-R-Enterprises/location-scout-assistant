import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import Dashboard from './components/Dashboard'

export default function App() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalysis = (data) => {
    setReport(data)
    setLoading(false)
    setError(null)
  }

  const handleReset = () => {
    setReport(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">LS</div>
            <h1 className="text-xl font-semibold text-white">Location Scout Assistant</h1>
          </div>
          {report && (
            <button
              onClick={handleReset}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              New Analysis
            </button>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!report && !loading && (
          <UploadForm
            onSubmit={() => setLoading(true)}
            onResult={handleAnalysis}
            onError={(e) => { setError(e); setLoading(false); }}
          />
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-32 gap-4">
            <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-lg">Analyzing screenplay...</p>
            <p className="text-gray-600 text-sm">Extracting scenes, finding locations, calculating routes</p>
          </div>
        )}

        {error && (
          <div className="max-w-xl mx-auto mt-16 p-6 bg-red-950/50 border border-red-800 rounded-xl">
            <h3 className="text-red-400 font-semibold mb-2">Analysis Failed</h3>
            <p className="text-red-300 text-sm">{error}</p>
            <button
              onClick={() => { setError(null); setLoading(false); }}
              className="mt-4 px-4 py-2 bg-red-800 hover:bg-red-700 rounded-lg text-sm text-white transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {report && !loading && <Dashboard report={report} />}
      </main>
    </div>
  )
}
