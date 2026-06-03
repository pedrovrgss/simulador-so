export interface MemoryBlockInfo {
  id: string
  occupied: boolean
  processId: `P${number}` | null
}

export interface MainMemoryInfo {
  totalBlocks: number
  usedBlocks: number
  blocks: MemoryBlockInfo[]
}
