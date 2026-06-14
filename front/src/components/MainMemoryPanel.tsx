import type { MemorySnapshot } from '../types/simulator'

function toHexAddr(mb: number): string {
  return '0x' + mb.toString(16).toUpperCase().padStart(4, '0')
}

function formatMb(mb: number): string {
  return mb >= 1024 ? `${(mb / 1024).toFixed(mb % 1024 === 0 ? 0 : 1)} GB` : `${mb} MB`
}

interface MainMemoryPanelProps {
  memory: MemorySnapshot
}

export function MainMemoryPanel({ memory }: MainMemoryPanelProps) {
  const freeMb = memory.totalMb - memory.usedMb
  const usagePercent = Math.round((memory.usedMb / memory.totalMb) * 100)

  return (
    <aside className="flex h-full w-[17rem] flex-col rounded-md border border-white/10 bg-white/4 p-3">
      <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">
        Memória principal
      </p>

      <div className="mt-2 flex flex-col gap-0.5">
        <div className="flex justify-between text-[0.68rem]">
          <span className="text-slate-400">Total</span>
          <span className="font-medium text-white">{formatMb(memory.totalMb)}</span>
        </div>
        <div className="flex justify-between text-[0.68rem]">
          <span className="text-slate-400">Em uso</span>
          <span className="font-medium text-sky-400">{formatMb(memory.usedMb)}</span>
        </div>
        <div className="flex justify-between text-[0.68rem]">
          <span className="text-slate-400">Livre</span>
          <span className="font-medium text-slate-300">{formatMb(freeMb)}</span>
        </div>
      </div>

      <div className="mt-2 h-1.5 overflow-hidden rounded-sm bg-white/8">
        <div
          className="h-full rounded-sm bg-sky-400"
          style={{ width: `${usagePercent}%` }}
        />
      </div>

      {/* Mapa de memória: cada segmento tem altura proporcional ao seu tamanho real */}
      <div className="mt-3 flex min-h-0 flex-1 gap-2">
        {/* Coluna de endereços */}
        <div className="flex flex-col py-0.5">
          {memory.blocks.map((block) => (
            <div
              key={block.id}
              className="flex items-start"
              style={{ flex: block.sizeMb }}
            >
              <span className="font-mono text-[0.58rem] leading-none text-slate-500">
                {toHexAddr(block.startMb)}
              </span>
            </div>
          ))}
        </div>

        {/* Coluna de segmentos */}
        <div className="flex flex-1 flex-col overflow-hidden rounded-sm border border-white/10">
          {memory.blocks.map((block) => (
            <div
              key={block.id}
              title={block.ownerPid ?? 'Livre'}
              className="flex items-center justify-between gap-1 border-b border-white/10 px-2 last:border-b-0"
              style={{
                flex: block.sizeMb,
                backgroundColor: block.color ? `${block.color}22` : 'rgba(255,255,255,0.03)',
              }}
            >
              <span
                className="truncate text-[0.62rem] font-medium"
                style={{ color: block.color ?? '#475569' }}
              >
                {block.ownerPid ?? 'livre'}
              </span>
              <span className="shrink-0 text-[0.58rem] text-slate-500">
                {formatMb(block.sizeMb)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
