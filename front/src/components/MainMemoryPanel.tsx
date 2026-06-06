import type { MemoryBlock, MemorySnapshot } from '../types/simulator'

interface Segment {
  ownerPid: string | null
  blockCount: number
  startBlock: number
  color: string | null
}

function groupSegments(blocks: MemoryBlock[]): Segment[] {
  if (blocks.length === 0) return []

  const segments: Segment[] = []
  let current: Segment = {
    ownerPid: blocks[0].ownerPid,
    blockCount: 1,
    startBlock: 0,
    color: blocks[0].color,
  }

  for (let i = 1; i < blocks.length; i++) {
    const block = blocks[i]
    if (block.ownerPid === current.ownerPid) {
      current.blockCount++
    } else {
      segments.push(current)
      current = { ownerPid: block.ownerPid, blockCount: 1, startBlock: i, color: block.color }
    }
  }
  segments.push(current)
  return segments
}

function toHexAddr(offsetMb: number): string {
  return '0x' + offsetMb.toString(16).toUpperCase().padStart(4, '0')
}

function formatMb(mb: number): string {
  return mb >= 1024 ? `${(mb / 1024).toFixed(0)} GB` : `${mb} MB`
}

interface MainMemoryPanelProps {
  memory: MemorySnapshot
}

export function MainMemoryPanel({ memory }: MainMemoryPanelProps) {
  const totalBlocks = memory.blocks.length
  const blockSizeMb = totalBlocks > 0 ? memory.totalMb / totalBlocks : 0
  const freeMb = memory.totalMb - memory.usedMb
  const usagePercent = Math.round((memory.usedMb / memory.totalMb) * 100)
  const segments = groupSegments(memory.blocks)

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

      <div className="mt-3 flex min-h-0 flex-1 gap-2">
        <div className="flex flex-col py-0.5">
          {segments.map((seg, i) => (
            <div key={i} className="flex items-start" style={{ flex: seg.blockCount }}>
              <span className="font-mono text-[0.58rem] leading-none text-slate-500">
                {toHexAddr(seg.startBlock * blockSizeMb)}
              </span>
            </div>
          ))}
        </div>

        <div className="flex flex-1 flex-col overflow-hidden rounded-sm border border-white/10">
          {segments.map((seg, i) => (
            <div
              key={i}
              title={seg.ownerPid ?? 'Livre'}
              className="flex items-center justify-between gap-1 border-b border-white/10 px-2 last:border-b-0"
              style={{
                flex: seg.blockCount,
                backgroundColor: seg.color ? `${seg.color}22` : 'rgba(255,255,255,0.03)',
              }}
            >
              <span
                className="truncate text-[0.62rem] font-medium"
                style={{ color: seg.color ?? '#475569' }}
              >
                {seg.ownerPid ?? 'livre'}
              </span>
              <span className="shrink-0 text-[0.58rem] text-slate-500">
                {formatMb(seg.blockCount * blockSizeMb)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
