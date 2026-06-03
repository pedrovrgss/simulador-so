import type { MainMemoryInfo } from '../types/memory'

interface MainMemoryPanelProps {
  memory: MainMemoryInfo
}

export function MainMemoryPanel({ memory }: MainMemoryPanelProps) {
  const usagePercent = Math.round((memory.usedBlocks / memory.totalBlocks) * 100)

  return (
    <aside className="w-[17rem] rounded-md border border-white/10 bg-white/4 p-3">
      <div className="flex items-end justify-between gap-3">
        <div>
          <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">
            Memoria principal
          </p>
          <p className="mt-1 text-sm font-semibold text-white">{usagePercent}% em uso</p>
        </div>
        <p className="text-[0.72rem] text-slate-400">
          {memory.usedBlocks}/{memory.totalBlocks}
        </p>
      </div>

      <div className="mt-3 h-1.5 overflow-hidden rounded-sm bg-white/8">
        <div
          className="h-full rounded-sm bg-sky-400"
          style={{ width: `${usagePercent}%` }}
        />
      </div>

      <div className="mt-3 grid grid-cols-4 gap-1.5">
        {memory.blocks.map((block) => (
          <div
            key={block.id}
            title={block.processId ?? 'Livre'}
            className={`flex h-10 items-end rounded-sm border px-1.5 py-1 ${
              block.occupied
                ? 'border-sky-400/30 bg-sky-400/14'
                : 'border-white/8 bg-white/4'
            }`}
          >
            <span className="truncate text-[0.62rem] text-slate-200">
              {block.processId ?? block.id}
            </span>
          </div>
        ))}
      </div>
    </aside>
  )
}
