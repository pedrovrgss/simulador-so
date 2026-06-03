import type { CSSProperties } from 'react'
import type { ProcessorInfo, ProcessorPhase } from '../types/processor'

interface CpuCardProps {
  cpu: ProcessorInfo
  accentColor: string
}

const PHASE_LABELS: Record<ProcessorPhase, string> = {
  fase_cpu_1: 'Fase 1 de CPU',
  fase_io: 'Fase de I/O',
  fase_cpu_2: 'Fase 2 de CPU',
  cpu_bound: 'CPU-bound',
}

export function CpuCard({ cpu, accentColor }: CpuCardProps) {
  const isActive = cpu.status === 'executando'
  const runningProcess = cpu.runningProcess
  const progressValue =
    isActive && runningProcess
      ? Math.max(
          0,
          Math.min(
            100,
            ((runningProcess.totalCycles - runningProcess.remainingCycles) /
              runningProcess.totalCycles) *
              100,
          ),
        )
      : 0

  return (
    <article
      className="h-[8.64rem] w-[8.64rem] rounded-md border border-white/10 bg-white/4 p-2.5"
      style={{ '--cpu-accent': accentColor } as CSSProperties}
    >
      <div className="flex h-full flex-col justify-between">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <p className="text-[0.58rem] uppercase tracking-[0.2em] text-slate-500">{cpu.label}</p>
            <div
              className="h-1 w-7 rounded-[2px]"
              style={{ backgroundColor: isActive ? accentColor : '#64748b' }}
            />
          </div>

          <div className="mt-0.5 flex items-center gap-1.5">
            <span
              className="h-2 w-2 rounded-[2px]"
              style={{ backgroundColor: isActive ? accentColor : '#64748b' }}
            />
            <span className="text-[0.55rem] uppercase tracking-[0.16em] text-slate-400">
              {isActive ? 'Ativa' : 'Livre'}
            </span>
          </div>
        </div>

        <div className="space-y-2">
          {isActive && runningProcess ? (
            <>
              <div className="space-y-1">
                <p className="text-[0.95rem] font-semibold leading-none text-white">
                  {runningProcess.id}
                </p>
                <p className="text-[0.82rem] leading-tight text-slate-200">
                  {PHASE_LABELS[runningProcess.phase]}
                </p>
              </div>

              <div className="space-y-1.5">
                <div className="h-1.5 w-full overflow-hidden rounded-sm bg-white/8">
                  <div
                    className="h-full rounded-sm"
                    style={{
                      width: `${progressValue}%`,
                      backgroundColor: accentColor,
                    }}
                  />
                </div>
                <p className="text-[0.8rem] leading-none text-slate-200">
                  <span className="font-semibold text-white">
                    {runningProcess.remainingCycles}
                  </span>{' '}
                  ciclos restantes
                </p>
              </div>
            </>
          ) : (
            <div className="space-y-1">
              <p className="text-sm font-semibold leading-none text-white">Livre</p>
              <p className="text-[0.72rem] leading-tight text-slate-400">Sem processo em execucao</p>
            </div>
          )}
        </div>
      </div>
    </article>
  )
}
