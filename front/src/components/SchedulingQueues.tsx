import type { QueueSnapshot, ProcessCard } from '../types/simulator'

function formatMb(mb: number): string {
  return mb >= 1024 ? `${mb / 1024}GB` : `${mb}MB`
}

function ProcessChip({ process }: { process: ProcessCard }) {
  return (
    <div
      className="flex shrink-0 items-center gap-1.5 rounded-sm border px-2 py-1.5"
      style={{
        backgroundColor: `${process.color}18`,
        borderColor: `${process.color}33`,
      }}
    >
      <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: process.color }} />
      <span className="text-[0.68rem] font-medium text-slate-200">{process.pid}</span>
      {process.memoryMb != null && (
        <span className="text-[0.58rem] text-slate-500">{formatMb(process.memoryMb)}</span>
      )}
    </div>
  )
}

function EmptySlot() {
  return <span className="text-[0.62rem] text-slate-700">vazia</span>
}

function Chips({ processes }: { processes: ProcessCard[] }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {processes.length === 0
        ? <EmptySlot />
        : processes.map(p => <ProcessChip key={p.pid} process={p} />)
      }
    </div>
  )
}

function DmaQueue({ queue }: { queue: QueueSnapshot }) {
  const activeSet = new Set(queue.activeProcessPids ?? [])
  const running = queue.processes.find(p => activeSet.has(p.pid)) ?? null
  const waiting = queue.processes.filter(p => !activeSet.has(p.pid))

  return (
    <div className="flex flex-col gap-2 rounded-md border border-white/10 bg-white/4 px-3 py-2.5">
      <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">{queue.title}</p>

      <div className="flex flex-wrap items-center gap-1.5">
        <div className="flex shrink-0 items-center gap-2 rounded-sm border border-white/8 bg-black/30 px-2.5 py-1.5">
          <span className="text-[0.55rem] uppercase tracking-[0.18em] text-slate-600">DMA</span>
          {running
            ? <ProcessChip process={running} />
            : <EmptySlot />
          }
        </div>

        {waiting.map(p => <ProcessChip key={p.pid} process={p} />)}
      </div>
    </div>
  )
}

function QueueRow({ queue }: { queue: QueueSnapshot }) {
  if (queue.activeProcessPids !== undefined) {
    return <DmaQueue queue={queue} />
  }

  return (
    <div className="flex flex-col gap-2 rounded-md border border-white/10 bg-white/4 px-3 py-2.5">
      <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">{queue.title}</p>
      <Chips processes={queue.processes} />
    </div>
  )
}

function FeedbackGroup({ queues }: { queues: QueueSnapshot[] }) {
  return (
    <div className="flex flex-col gap-2 rounded-md border border-white/10 bg-white/4 px-3 py-2.5">
      <div className="flex items-baseline gap-2">
        <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">Feedback</p>
        <span className="text-[0.58rem] text-slate-600">Quantum 2</span>
      </div>

      <div className="flex flex-col gap-1.5">
        {queues.map((queue) => (
          <div
            key={queue.id}
            className="flex items-center gap-2 rounded-sm border border-white/8 bg-black/10 px-2.5 py-2"
          >
            <p className="shrink-0 text-[0.6rem] font-medium text-slate-400">{queue.kind}</p>
            <Chips processes={queue.processes} />
          </div>
        ))}
      </div>
    </div>
  )
}

interface SchedulingQueuesProps {
  queues: QueueSnapshot[]
}

export function SchedulingQueues({ queues }: SchedulingQueuesProps) {
  const feedbackQueues = queues.filter(q => q.title.toLowerCase().includes('feedback'))
  const otherQueues = queues.filter(q => !q.title.toLowerCase().includes('feedback'))

  const before = otherQueues.slice(0, 1)
  const after = otherQueues.slice(1)

  return (
    <div className="flex h-full w-full flex-col gap-2">
      {before.map(q => <QueueRow key={q.id} queue={q} />)}
      {feedbackQueues.length > 0 && <FeedbackGroup queues={feedbackQueues} />}
      {after.map(q => <QueueRow key={q.id} queue={q} />)}
    </div>
  )
}
