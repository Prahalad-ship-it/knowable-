import { useEffect, useState } from 'react'
import { Send } from 'lucide-react'

export default function QueryInput({ value, onSubmit, status }) {
  const [input, setInput] = useState(value)

  useEffect(() => {
    setInput(value)
  }, [value])

  const handleSubmit = (event) => {
    event.preventDefault()
    
    // Prevent submitting empty or purely whitespace queries
    if (!input.trim()) return

    // Pass the clean text string up to your parent handler (which calls api.js)
    if (onSubmit) {
      onSubmit(input.trim())
    }
  }

  const isSystemBusy = status === 'streaming' || status === 'loading'

  return (
    <form onSubmit={handleSubmit} className="rounded-[2rem] border border-episteme-border bg-white/5 p-5 shadow-glow transition">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <div className="min-w-0 flex-1">
          <label className="text-sm font-medium uppercase tracking-[0.3em] text-episteme-subtext" htmlFor="query-input">
            Calibrated Omnibar
          </label>
          <input
            id="query-input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            className="mt-3 w-full rounded-[1.5rem] border border-episteme-border bg-episteme-bg px-5 py-4 text-lg text-white outline-none transition focus:border-episteme-accent focus:ring-2 focus:ring-episteme-accent/20"
            placeholder="Ask Episteme something high-stakes..."
            disabled={isSystemBusy}
          />
        </div>

        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-[1.5rem] bg-episteme-accent px-6 py-4 text-sm font-semibold text-white transition hover:bg-[#5d7bf9] disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSystemBusy}
        >
          <Send className="h-4 w-4" />
          {status === 'loading' ? 'Evaluating...' : 'Submit'}
        </button>
      </div>

      <p className="mt-4 text-sm text-episteme-subtext">
        Episteme will evaluate your query across Data Sufficiency, Reasoning Certainty, and Edge Case Risk before responding.
      </p>
    </form>
  )
}