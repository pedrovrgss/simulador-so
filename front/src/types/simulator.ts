export type ProcessClass = 'tempo_real' | 'usuario'
export type ProcessPhase =
  | 'fase_cpu_1'
  | 'fase_io'
  | 'fase_cpu_2'
  | 'cpu_bound'

export interface ProcessCard {
  pid: string
  name: string
  color: string
  classLabel: string
  queueLabel: string
  memoryMb?: number
}

export interface CpuSlot {
  id: string
  label: string
  runningProcess: ProcessCard | null
  quantumLeft: number | null
  remainingBurst: number | null
  totalBurst: number | null
  phase: ProcessPhase | null
}

export interface QueueSnapshot {
  id: string
  title: string
  kind: string
  processes: ProcessCard[]
  activeProcessPids?: string[] | null
}

export interface MemoryBlock {
  id: string
  label: string
  occupied: boolean
  ownerPid: string | null
  color: string | null
}

export interface MemorySnapshot {
  totalMb: number
  usedMb: number
  blocks: MemoryBlock[]
}

export interface DiskSnapshot {
  id: string
  label: string
  status: 'livre' | 'reservado' | 'io'
  ownerProcess: ProcessCard | null
  activeProcess: ProcessCard | null
  waitingQueue: ProcessCard[]
}

export interface EventEntry {
  id: string
  time: number
  message: string
}

export interface SimulatorSnapshot {
  clock: number
  cpus: CpuSlot[]
  queues: QueueSnapshot[]
  memory: MemorySnapshot
  disks: DiskSnapshot[]
  eventLog: EventEntry[]
}
