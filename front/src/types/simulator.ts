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
  startMb: number   // endereco de inicio em MiB
  sizeMb: number    // tamanho real em MiB
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
  // Processo atualmente fazendo I/O neste drive (null se livre).
  activeIoProcess: ProcessCard | null
  // Processos que foram carregados na RAM a partir deste disco.
  inMemory: ProcessCard[]
  // Processos que ainda estao so no armazenamento secundario (aguardando RAM).
  onDiskOnly: ProcessCard[]
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
  warnings: string[]
}
