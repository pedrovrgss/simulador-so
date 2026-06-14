import type { SimulatorSnapshot } from '../types/simulator'

// Dados de demo usados enquanto o backend nao esta conectado.
// Prefixos: TR-nnn = tempo real (FCFS, priority 0), IO-nnn = usuario (feedback, priority 1).

export const fallbackSnapshot: SimulatorSnapshot = {
  clock: 18,
  cpus: [
    {
      id: 'cpu-1',
      label: 'CPU 1',
      runningProcess: {
        pid: 'TR-01',
        name: 'Controle de voo',
        color: '#ff6b57',
        classLabel: 'Tempo real',
        queueLabel: 'FCFS',
      },
      quantumLeft: null,
      remainingBurst: 4,
      totalBurst: 10,
      phase: 'fase_cpu_1',
    },
    {
      id: 'cpu-2',
      label: 'CPU 2',
      runningProcess: {
        pid: 'IO-07',
        name: 'Editor',
        color: '#42d392',
        classLabel: 'I/O Bound',
        queueLabel: 'Feedback 1',
      },
      quantumLeft: 1,
      remainingBurst: 2,
      totalBurst: 8,
      phase: 'fase_cpu_2',
    },
    {
      id: 'cpu-3',
      label: 'CPU 3',
      runningProcess: {
        pid: 'IO-03',
        name: 'Compilador',
        color: '#5cc8ff',
        classLabel: 'CPU Bound',
        queueLabel: 'Feedback 2',
      },
      quantumLeft: 2,
      remainingBurst: 5,
      totalBurst: 12,
      phase: 'cpu_bound',
    },
    {
      id: 'cpu-4',
      label: 'CPU 4',
      runningProcess: null,
      quantumLeft: null,
      remainingBurst: null,
      totalBurst: null,
      phase: null,
    },
  ],
  queues: [
    {
      id: 'fila-tr',
      title: 'FCFS',
      kind: 'FCFS',
      processes: [
        {
          pid: 'TR-02',
          name: 'Monitoramento',
          color: '#f59e0b',
          classLabel: 'Tempo real',
          queueLabel: 'FCFS',
          memoryMb: 1024,
        },
      ],
    },
    {
      id: 'fila-f1',
      title: 'Fila de feedback 1',
      kind: 'Nível 1',
      processes: [
        {
          pid: 'IO-11',
          name: 'Planilhas',
          color: '#7dd3fc',
          classLabel: 'I/O Bound',
          queueLabel: 'Feedback 1',
          memoryMb: 1024,
        },
        {
          pid: 'IO-12',
          name: 'Render',
          color: '#c084fc',
          classLabel: 'I/O Bound',
          queueLabel: 'Feedback 1',
          memoryMb: 2048,
        },
      ],
    },
    {
      id: 'fila-f2',
      title: 'Fila de feedback 2',
      kind: 'Nível 2',
      processes: [
        {
          pid: 'IO-08',
          name: 'Navegador',
          color: '#34d399',
          classLabel: 'I/O Bound',
          queueLabel: 'Feedback 2',
          memoryMb: 1024,
        },
      ],
    },
    {
      id: 'fila-f3',
      title: 'Fila de feedback 3',
      kind: 'Nível 3',
      processes: [
        {
          pid: 'IO-01',
          name: 'Backup',
          color: '#f472b6',
          classLabel: 'I/O Bound',
          queueLabel: 'Feedback 3',
          memoryMb: 2048,
        },
      ],
    },
    {
      id: 'fila-dma',
      title: 'Aguardando I/O',
      kind: 'Direct Memory Access',
      activeProcessPids: ['IO-05'],
      processes: [
        {
          pid: 'IO-05',
          name: 'Banco',
          color: '#fb7185',
          classLabel: 'I/O Bound',
          queueLabel: 'Disco 2',
          memoryMb: 1024,
        },
        {
          pid: 'IO-06',
          name: 'Relatorios',
          color: '#a3e635',
          classLabel: 'I/O Bound',
          queueLabel: 'Disco 4',
          memoryMb: 1024,
        },
      ],
    },
    {
      id: 'fila-memoria',
      title: 'Aguardando memória',
      kind: 'Carga DMA',
      activeProcessPids: ['IO-09'],
      processes: [
        {
          pid: 'IO-09',
          name: 'Streaming',
          color: '#818cf8',
          classLabel: 'I/O Bound',
          queueLabel: 'Aguardando',
          memoryMb: 4096,
        },
      ],
    },
    {
      id: 'fila-finalizados',
      title: 'Finalizados',
      kind: 'Concluidos',
      processes: [
        {
          pid: 'IO-02',
          name: 'Logs',
          color: '#94a3b8',
          classLabel: 'I/O Bound',
          queueLabel: 'Finalizado',
          memoryMb: 1024,
        },
      ],
    },
  ],
  memory: {
    totalMb: 32768,
    usedMb: 23216,
    // Segmentos reais: startMb = endereco de inicio, sizeMb = tamanho exato do processo.
    // First Fit aloca no primeiro buraco contíguo suficiente; a altura e proporcional a sizeMb.
    blocks: [
      { id: 'seg-0',  startMb: 0,     sizeMb: 512,   occupied: true,  ownerPid: 'TR-01', color: '#ff6b57' },
      { id: 'seg-1',  startMb: 512,   sizeMb: 1024,  occupied: true,  ownerPid: 'IO-02', color: '#94a3b8' },
      { id: 'seg-2',  startMb: 1536,  sizeMb: 2048,  occupied: true,  ownerPid: 'IO-03', color: '#5cc8ff' },
      { id: 'seg-3',  startMb: 3584,  sizeMb: 4096,  occupied: true,  ownerPid: 'IO-04', color: '#a78bfa' },
      { id: 'seg-4',  startMb: 7680,  sizeMb: 8192,  occupied: true,  ownerPid: 'IO-06', color: '#a3e635' },
      { id: 'seg-5',  startMb: 15872, sizeMb: 1200,  occupied: true,  ownerPid: 'IO-07', color: '#42d392' },
      { id: 'seg-6',  startMb: 17072, sizeMb: 4096,  occupied: true,  ownerPid: 'IO-10', color: '#38bdf8' },
      { id: 'seg-7',  startMb: 21168, sizeMb: 2048,  occupied: true,  ownerPid: 'IO-12', color: '#c084fc' },
      { id: 'seg-8',  startMb: 23216, sizeMb: 9552,  occupied: false, ownerPid: null,    color: null },
    ],
  },
  disks: [
    {
      id: 'disk-1',
      label: 'Disco 1',
      activeIoProcess: { pid: 'IO-05', name: 'Banco', color: '#fb7185', classLabel: 'I/O Bound', queueLabel: 'Disco 1' },
      inMemory: [
        { pid: 'TR-01', name: 'Controle', color: '#ff6b57', classLabel: 'Tempo real', queueLabel: 'FCFS' },
        { pid: 'IO-05', name: 'Banco',    color: '#fb7185', classLabel: 'I/O Bound', queueLabel: 'Disco 1' },
      ],
      onDiskOnly: [],
    },
    {
      id: 'disk-2',
      label: 'Disco 2',
      activeIoProcess: { pid: 'IO-06', name: 'Relatorios', color: '#a3e635', classLabel: 'I/O Bound', queueLabel: 'Disco 2' },
      inMemory: [
        { pid: 'IO-07', name: 'Editor',    color: '#42d392', classLabel: 'I/O Bound', queueLabel: 'Feedback 1' },
        { pid: 'IO-06', name: 'Relatorios',color: '#a3e635', classLabel: 'I/O Bound', queueLabel: 'Disco 2' },
      ],
      onDiskOnly: [],
    },
    {
      id: 'disk-3',
      label: 'Disco 3',
      activeIoProcess: null,
      inMemory: [
        { pid: 'IO-03', name: 'Compilador', color: '#5cc8ff', classLabel: 'CPU Bound', queueLabel: 'Feedback 2' },
        { pid: 'IO-08', name: 'Navegador',  color: '#34d399', classLabel: 'I/O Bound', queueLabel: 'Feedback 2' },
      ],
      onDiskOnly: [
        { pid: 'IO-09', name: 'Streaming', color: '#818cf8', classLabel: 'I/O Bound', queueLabel: 'Aguardando' },
      ],
    },
    {
      id: 'disk-4',
      label: 'Disco 4',
      activeIoProcess: null,
      inMemory: [
        { pid: 'TR-02', name: 'Monitor',  color: '#f59e0b', classLabel: 'Tempo real', queueLabel: 'FCFS' },
        { pid: 'IO-11', name: 'Planilhas',color: '#7dd3fc', classLabel: 'I/O Bound', queueLabel: 'Feedback 1' },
      ],
      onDiskOnly: [],
    },
  ],
  eventLog: [
    { id: 'e1', time: 14, message: 'TR-01: criado e alocado na memoria principal.' },
    { id: 'e2', time: 15, message: 'IO-07: entrou na CPU 2 a partir da fila de feedback 1.' },
    { id: 'e3', time: 16, message: 'IO-05: bloqueado para operacao de disco no Disco 1.' },
    { id: 'e4', time: 17, message: 'IO-03: consumiu o quantum e retornou para feedback 2.' },
    { id: 'e5', time: 18, message: 'CPU 4: ficou ociosa por ausencia de processo pronto.' },
  ],
}
