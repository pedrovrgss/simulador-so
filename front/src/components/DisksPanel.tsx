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

function DiskCard({ disk }: { disk: DiskSnapshot }) {
  const process = disk.status === 'io' ? disk.activeProcess : disk.ownerProcess
  const statusText = disk.status === 'io' && process
    ? `Em I/O: ${process.pid}`
    : disk.status === 'reservado' && process
      ? `Reservado por ${process.pid}`
      : 'Livre'

  return (
    <div className="flex min-w-0 flex-col gap-2 rounded-md border border-white/10 bg-white/4 p-2.5">
      <p className="whitespace-nowrap text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">{disk.label}</p>

      <div className="flex flex-col gap-2">
        <div className="flex flex-col gap-1">
          <span className="whitespace-nowrap text-[0.52rem] uppercase tracking-[0.18em] text-slate-700">estado</span>
          <span className="text-[0.68rem] font-semibold text-slate-300">
            {statusText}
          </span>
        </div>

        <div className="flex flex-col gap-1">
          <span className="whitespace-nowrap text-[0.52rem] uppercase tracking-[0.18em] text-slate-700">processo</span>
          <div className="flex flex-wrap gap-1">
            {process
              ? <ProcessChip process={process} />
              : <span className="text-[0.6rem] text-slate-700">—</span>
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
