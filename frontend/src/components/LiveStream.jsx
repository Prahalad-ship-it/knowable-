import { Activity, BookOpen, ShieldCheck, AlertTriangle } from 'lucide-react'

const phases = [
  {
    title: 'Data Sufficiency Evaluation',
    description: 'Checking facts, sources and available domain knowledge.',
    icon: BookOpen
  },
  {
    title: 'Reasoning Certainty Audit',
    description: 'Ensuring logic is sound and inference is not overreaching.',
    icon: ShieldCheck
  },
  {
    title: 'Edge Case Risk Assessment',
    description: 'Finding scenarios where the answer could fail or mislead.',
    icon: AlertTriangle
  }
]

export default function LiveStream({ phase, status }) {
  return (
    <section className="rounded-[2rem] border border-episteme-border bg-white/5 p-6 shadow-glow">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-episteme-subtext">Pre-Computation Live Stream</p>
          <h2 className="text-2xl font-semibold text-white">Episteme is auditing your prompt</h2>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-episteme-border px-3 py-2 text-sm text-episteme-subtext">
          <Activity className="h-4 w-4 text-episteme-accent" />
          {status === 'streaming' ? 'Streaming...' : 'Paused'}
        </div>
      </div>

      <div className="mt-8 space-y-4">
        {phases.map((item, index) => {
          const active = phase === index + 1
          const completed = phase > index + 1
          const Icon = item.icon

          return (
            <div
              key={item.title}
              className={`rounded-3xl border px-5 py-5 transition ${
                active ? 'border-episteme-accent bg-episteme-accent/10' : 'border-episteme-border bg-white/5'
              } ${completed ? 'opacity-80' : 'opacity-100'}`}
            >
              <div className="flex items-start gap-4">
                <span className={`mt-1 grid h-11 w-11 place-items-center rounded-2xl ${
                  active ? 'bg-episteme-accent text-episteme-bg' : 'bg-white/5 text-episteme-accent'
                }`}>
                  <Icon className="h-5 w-5" />
                </span>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3 text-sm uppercase tracking-[0.25em] text-episteme-subtext">
                    <span>{item.title}</span>
                    <span>{completed ? 'Done' : active ? 'In progress' : 'Waiting'}</span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-episteme-text">{item.description}</p>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-episteme-border">
                    <div
                      className={`h-full rounded-full bg-episteme-accent transition-all duration-500 ${
                        completed ? 'w-full' : active ? 'w-2/3' : 'w-0'
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
