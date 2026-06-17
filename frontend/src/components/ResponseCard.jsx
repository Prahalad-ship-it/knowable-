import { CheckCircle2, ShieldCheck, BookOpen, AlertTriangle } from 'lucide-react'

function StatPill({ label, value, color }) {
  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-center justify-between text-episteme-subtext">
        <span>{label}</span>
        <span className="font-semibold text-white">{value}/10</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-episteme-border">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value * 10}%` }} />
      </div>
    </div>
  )
}

function ProgressRing({ value, label }) {
  const radius = 46
  const stroke = 8
  const normalized = Math.min(100, Math.max(0, value * 10))
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (normalized / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-3 rounded-3xl border border-episteme-border bg-white/5 p-5 text-center">
      <svg className="h-32 w-32" viewBox="0 0 108 108">
        <circle cx="54" cy="54" r={radius} stroke="#1c2634" strokeWidth={stroke} fill="none" />
        <circle
          cx="54"
          cy="54"
          r={radius}
          stroke="#6f8cff"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 54 54)"
          fill="none"
        />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" className="text-3xl font-semibold fill-white">
          {normalized}%
        </text>
      </svg>
      <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">{label}</p>
    </div>
  )
}

export default function ResponseCard({ data, status }) {
  return (
    <section className="rounded-[2rem] border border-episteme-border bg-white/5 p-6 shadow-glow">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">Episteme Response</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">Calibrated conclusion with explicit gaps and next steps</h2>
        </div>
        <div className="inline-flex items-center gap-3 rounded-full bg-episteme-border px-4 py-2 text-sm text-episteme-subtext">
          <CheckCircle2 className="h-4 w-4 text-episteme-accent" />
          {status === 'ready' ? 'Ready' : 'Waiting on evaluation'}
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[0.6fr_0.4fr]">
        <div className="space-y-6">
          <div className="rounded-[1.75rem] border border-episteme-border bg-episteme-bg/80 p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">Overall Calibration Score</p>
                <p className="mt-2 text-4xl font-semibold text-white">{data.scores.overall * 10}%</p>
              </div>
              <div className="rounded-3xl bg-episteme-accent/10 px-4 py-2 text-sm font-semibold text-episteme-accent">
                {data.scores.overall >= 7 ? 'High confidence' : data.scores.overall >= 5 ? 'Moderate confidence' : 'Low confidence'}
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-episteme-subtext">{data.scores.justification}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <StatPill label="Sufficiency" value={data.scores.data_sufficiency} color="bg-episteme-accent" />
            <StatPill label="Certainty" value={data.scores.reasoning_certainty} color="bg-episteme-success" />
            <StatPill label="Risk" value={10 - data.scores.reasoning_certainty} color="bg-episteme-warning" />
          </div>

          <div className="space-y-6 rounded-[1.75rem] border border-episteme-border bg-episteme-bg/80 p-6 shadow-sm">
            <div className="flex items-center gap-3 text-sm uppercase tracking-[0.3em] text-episteme-subtext">
              <BookOpen className="h-4 w-4 text-episteme-accent" />
              <span>Knowledge gaps & assumptions</span>
            </div>
            <div className="space-y-3">
              {data.gaps.map((gap, index) => (
                <div key={index} className="rounded-3xl border border-episteme-border bg-white/5 p-4 text-sm text-episteme-text">
                  {gap}
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6 rounded-[1.75rem] border border-episteme-border bg-episteme-bg/80 p-6 shadow-sm">
            <div className="flex items-center gap-3 text-sm uppercase tracking-[0.3em] text-episteme-subtext">
              <ShieldCheck className="h-4 w-4 text-episteme-accent" />
              <span>Resolution plan</span>
            </div>
            <div className="space-y-3">
              {data.resolutions.map((resolution, index) => (
                <div key={index} className="flex items-start gap-3 rounded-3xl border border-episteme-border bg-white/5 p-4 text-sm">
                  <span className="mt-1 inline-flex h-8 w-8 items-center justify-center rounded-2xl bg-episteme-success/10 text-episteme-success">
                    {index + 1}
                  </span>
                  <p className="leading-6 text-episteme-text">{resolution}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <ProgressRing value={data.scores.overall} label="Confidence Meter" />
          <div className="rounded-[1.75rem] border border-episteme-border bg-episteme-bg/80 p-6 shadow-sm">
            <div className="flex items-center gap-3 text-sm uppercase tracking-[0.3em] text-episteme-subtext">
              <AlertTriangle className="h-4 w-4 text-episteme-warning" />
              <span>Calibrated response</span>
            </div>
            <p className="mt-5 text-sm leading-7 text-episteme-text">{data.calibrated_response}</p>
          </div>
        </div>
      </div>
    </section>
  )
}
