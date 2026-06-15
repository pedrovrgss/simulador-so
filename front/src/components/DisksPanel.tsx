import type { DiskSnapshot, ProcessCard } from '../types/simulator'

function ProcessChip({ process }: { process: ProcessCard }) {
  return (
    <div
      className="flex shrink-0 items-center gap-1.5 rounded-sm border px-1.5 py-1"
      style={{
        backgroundColor: `${process.color}18`,
        borderColor: `${process.color}33`,
      }}
    >
      <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ backgroundColor: process.color }} />
      <span className="text-[0.62rem] font-medium text-slate-200">{process.pid}</span>
    </div>
  )
}

function IoActiveChip({ process }: { process: ProcessCard }) {
  return (
    <div
      className="flex shrink-0 items-center gap-1.5 rounded-sm border px-1.5 py-1"
      style={{
        backgroundColor: `${process.color}25`,
        borderColor: `${process.color}66`,
      }}
    >
      <span
        className="h-1.5 w-1.5 shrink-0 animate-pulse rounded-full"
        style={{ backgroundColor: process.color }}
      />
      <span className="text-[0.6rem] font-semibold" style={{ color: process.color }}>
        {process.pid}
      </span>
    </div>
  )
}

function Empty() {
  return <span className="text-[0.6rem] text-slate-700">—</span>
}

function DiskCard({ disk }: { disk: DiskSnapshot }) {
  return (
    <div className="relative flex min-w-0 flex-col gap-2 rounded-md border border-white/10 bg-white/4 p-2.5">
      <div className="flex items-center justify-between gap-2">
        <p className="whitespace-nowrap text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">
          {disk.label}
        </p>

        {disk.activeIoProcess ? (
          <div className="flex items-center gap-1.5">
            <span className="text-[0.52rem] uppercase tracking-[0.14em] text-slate-600">I/O</span>
            <IoActiveChip process={disk.activeIoProcess} />
          </div>
        ) : (
          <span className="text-[0.52rem] uppercase tracking-[0.14em] text-slate-700">livre</span>
        )}
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex flex-col gap-1">
          <span className="whitespace-nowrap text-[0.52rem] uppercase tracking-[0.18em] text-slate-700">
            em memória
          </span>
          <div className="flex flex-wrap gap-1">
            {disk.inMemory.length > 0
              ? disk.inMemory.map(p => <ProcessChip key={p.pid} process={p} />)
              : <Empty />
            }
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <span className="whitespace-nowrap text-[0.52rem] uppercase tracking-[0.18em] text-slate-700">
            somente em disco
          </span>
          <div className="flex flex-wrap gap-1">
            {disk.onDiskOnly.length > 0
              ? disk.onDiskOnly.map(p => <ProcessChip key={p.pid} process={p} />)
              : <Empty />
            }
          </div>
        </div>
      </div>
    </div>
  )
}

interface DisksPanelProps {
  disks: DiskSnapshot[]
}

export function DisksPanel({ disks }: DisksPanelProps) {
  return (
    <div className="grid h-full min-w-[22rem] grid-cols-2 gap-2 rounded-md border border-white/10 bg-white/4 p-2">
      {disks.map(disk => (
        <DiskCard key={disk.id} disk={disk} />
      ))}
    </div>
  )
}
