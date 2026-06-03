export type ProcessorStatus = 'executando' | 'ociosa'

export type ProcessorPhase =
  | 'fase_cpu_1'
  | 'fase_io'
  | 'fase_cpu_2'
  | 'cpu_bound'

export type ProcessId = `P${number}`

export interface RunningProcessInfo {
  id: ProcessId
  phase: ProcessorPhase
  remainingCycles: number
  totalCycles: number
}

export interface ProcessorInfo {
  id: string
  label: string
  status: ProcessorStatus
  runningProcess: RunningProcessInfo | null
}
