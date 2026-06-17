import { useMemo, useState } from 'react'
import { Cpu, ShieldCheck, AlertTriangle, Sparkles, BookOpen, CheckCircle2 } from 'lucide-react'
import { mockQueries } from './mockData'
import { queryEpisteme } from './api'
import LiveStream from './components/LiveStream'
import ResponseCard from './components/ResponseCard'
import QueryInput from './components/QueryInput'

const initialQuery = mockQueries[0]

function App() {
  const [query, setQuery] = useState(initialQuery.question)
  const [activeExample, setActiveExample] = useState(initialQuery.id)
  const [result, setResult] = useState(initialQuery.result)
  const [status, setStatus] = useState('idle')
  const [phase, setPhase] = useState(0)
  const [error, setError] = useState(null)

  const currentExample = useMemo(() => mockQueries.find((item) => item.id === activeExample), [activeExample])

  const handleSubmit = async (input) => {
    if (!input.trim()) return
    setQuery(input)
    setStatus('streaming')
    setPhase(0)
    setError(null)

    const phases = [
      { title: 'Data Sufficiency Evaluation', icon: BookOpen },
      { title: 'Reasoning Certainty Audit', icon: ShieldCheck },
      { title: 'Edge Case Risk Assessment', icon: AlertTriangle }
    ]

    for (let index = 0; index < phases.length; index += 1) {
      await new Promise((resolve) => setTimeout(resolve, 900))
      setPhase(index + 1)
    }

    try {
      const response = await queryEpisteme(input)
      setResult(response)
      setStatus('ready')
    } catch (err) {
      setError(err.message)
      setStatus('error')
      setResult(currentExample.result)
    }
  }

  const handleExampleClick = (example) => {
    setActiveExample(example.id)
    setQuery(example.question)
    setResult(example.result)
    setStatus('ready')
    setPhase(0)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-episteme-bg">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-3 rounded-full border border-episteme-border bg-white/5 px-4 py-2 text-sm text-episteme-subtext shadow-sm backdrop-blur-sm">
              <Cpu className="h-4 w-4 text-episteme-accent" />
              Calibrated Clarity for high-stakes AI
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">Episteme</p>
                <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                  The AI agent that knows what it doesn’t know.
                </h1>
              </div>
              <p className="max-w-2xl text-lg leading-8 text-episteme-subtext">
                Build confidence with an AI system that audits its own knowledge across Data Sufficiency, Reasoning Certainty, and Edge Case Risks before delivering any answer.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:w-[420px]">
            <div className="rounded-3xl border border-episteme-border bg-white/5 p-5 shadow-glow">
              <p className="text-sm uppercase tracking-[0.25em] text-episteme-subtext">Calibrated Output</p>
              <p className="mt-3 text-2xl font-semibold text-white">Epistemic score, gaps, and a resolution plan.</p>
            </div>
            <div className="rounded-3xl border border-episteme-border bg-white/5 p-5 shadow-glow">
              <p className="text-sm uppercase tracking-[0.25em] text-episteme-subtext">Workflow</p>
              <p className="mt-3 text-2xl font-semibold text-white">Query, watch the audit stream, and act on what’s uncertain.</p>
            </div>
          </div>
        </header>

        <section className="grid gap-8 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-8">
            <QueryInput value={query} onSubmit={handleSubmit} status={status} />
            <LiveStream phase={phase} status={status} />
            <ResponseCard data={result} status={status} />
          </div>

          <aside className="space-y-6 rounded-3xl border border-episteme-border bg-white/5 p-6 shadow-glow">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">Live Demos</p>
                <h2 className="text-xl font-semibold text-white">Risk-aware Scenarios</h2>
              </div>
              <Sparkles className="h-6 w-6 text-episteme-accent" />
            </div>
            {error ? (
              <div className="rounded-3xl border border-episteme-danger/20 bg-episteme-danger/10 p-4 text-sm text-episteme-text">
                <p className="font-semibold text-episteme-danger">Unable to fetch an answer.</p>
                <p>{error}</p>
              </div>
            ) : null}

            <div className="space-y-4">
              {mockQueries.map((example) => (
                <button
                  key={example.id}
                  type="button"
                  onClick={() => handleExampleClick(example)}
                  className={`w-full rounded-3xl border px-4 py-4 text-left transition ${
                    example.id === activeExample
                      ? 'border-episteme-accent bg-episteme-accent/10 text-white shadow-md'
                      : 'border-episteme-border bg-white/5 text-episteme-text hover:border-episteme-accent hover:bg-episteme-accent/5'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-medium">{example.title}</span>
                    <span className="rounded-full bg-episteme-border px-3 py-1 text-xs uppercase tracking-[0.25em] text-episteme-subtext">
                      {example.tag}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-episteme-subtext">{example.question}</p>
                </button>
              ))}
            </div>
          </aside>
        </section>
      </div>
    </div>
  )
}

export default App
