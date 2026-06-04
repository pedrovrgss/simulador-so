import type { EventEntry } from '../types/simulator'

interface EventLogProps {
  events: EventEntry[]
}

export function EventLog({ events }: EventLogProps) {
  const sorted = [...events].sort((a, b) => b.time - a.time)

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-md border border-white/10 bg-black/60">
      <div className="flex shrink-0 items-center border-b border-white/8 bg-white/4 px-3 py-1.5">
        <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">log de eventos</p>
      </div>

      <div className="flex flex-col-reverse gap-0.5 overflow-y-auto p-2">
        {sorted.length === 0 ? (
          <span className="font-mono text-[0.62rem] text-slate-700">_</span>
        ) : (
          sorted.map((entry) => (
            <div key={entry.id} className="flex gap-2">
              <span className="shrink-0 font-mono text-[0.6rem] text-slate-600">
                [{String(entry.time).padStart(3, '0')}]
              </span>
              <span className="font-mono text-[0.62rem] leading-tight text-slate-400">
                {entry.message}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
