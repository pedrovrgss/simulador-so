import type { CpuSlot, ProcessPhase } from '../types/simulator'

interface CpuCardProps {
  cpu: CpuSlot
}

const PHASE_LABELS: Record<ProcessPhase, string> = {
  fase_cpu_1: 'Fase 1 de CPU',
  fase_io: 'Fase de I/O',
  fase_cpu_2: 'Fase 2 de CPU',
  cpu_bound: 'CPU-bound',
}

export function CpuCard({ cpu }: CpuCardProps) {
  const process = cpu.runningProcess
  const isActive = process !== null
  const color = process?.color ?? null
  const totalCycles = cpu.totalBurst ?? 0
  const remainingCycles = cpu.remainingBurst ?? 0

  const progress =
    isActive && totalCycles > 0
      ? Math.max(0, Math.min(100,
          ((totalCycles - remainingCycles) / totalCycles) * 100,
        ))
      : 0

  return (
    <article
      className="w-[8.64rem] rounded-md border border-white/10 p-2.5 transition-colors"
      style={{
        backgroundColor: color ? `${color}12` : 'rgba(255,255,255,0.04)',
        borderColor: color ? `${color}33` : undefined,
      }}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">{cpu.label}</p>
        <div className="flex items-center gap-1">
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ backgroundColor: color ?? '#334155' }}
          />
          <span
            className="text-[0.55rem] uppercase tracking-[0.14em]"
            style={{ color: color ?? '#64748b' }}
          >
            {isActive ? 'ativa' : 'livre'}
          </span>
        </div>
      </div>

      <div className="mt-3">
        {isActive && process ? (
          <>
            <p
              className="text-[0.95rem] font-semibold leading-none"
              style={{ color: color ?? '#fff' }}
            >
              {process.pid}
            </p>
            <p className="mt-1 text-[0.68rem] leading-tight text-slate-400">
              {cpu.phase ? PHASE_LABELS[cpu.phase] : 'Executando'}
            </p>

            <div className="mt-3 space-y-1.5">
              <div className="h-1.5 w-full overflow-hidden rounded-sm bg-white/8">
                <div
                  className="h-full rounded-sm transition-all"
                  style={{ width: `${progress}%`, backgroundColor: color ?? '#fff' }}
                />
              </div>
              <div className="flex justify-between text-[0.62rem]">
                <span className="text-slate-500">ciclos</span>
                <span className="text-slate-300">
                  <span className="font-medium text-white">{remainingCycles}</span>
                  {' / '}
                  {totalCycles}
                </span>
              </div>
            </div>
          </>
        ) : (
          <p className="text-[0.72rem] text-slate-600">Sem processo</p>
        )}
      </div>
    </article>
  )
}
