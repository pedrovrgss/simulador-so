export interface MemoryBlockInfo {
  id: string
  occupied: boolean
  processId: `P${number}` | null
  color?: string | null
}

export interface MainMemoryInfo {
  totalBlocks: number
  usedBlocks: number
  totalMb: number
  blocks: MemoryBlockInfo[]
}
