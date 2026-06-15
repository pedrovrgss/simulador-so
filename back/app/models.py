from pydantic import BaseModel


class ProcessCard(BaseModel):
    pid: str
    name: str
    color: str
    classLabel: str
    queueLabel: str
    memoryMb: int | None = None


class CpuSlot(BaseModel):
    id: str
    label: str
    runningProcess: ProcessCard | None = None
    quantumLeft: int | None = None
    remainingBurst: int | None = None
    totalBurst: int | None = None
    phase: str | None = None


class QueueSnapshot(BaseModel):
    id: str
    title: str
    kind: str
    processes: list[ProcessCard]
    activeProcessPids: list[str] | None = None


class MemoryBlock(BaseModel):
    id: str
    startMb: int   # endereco de inicio do segmento em MiB
    sizeMb: int    # tamanho real do segmento em MiB
    occupied: bool
    ownerPid: str | None = None
    color: str | None = None


class MemorySnapshot(BaseModel):
    totalMb: int
    usedMb: int
    blocks: list[MemoryBlock]


class DiskSnapshot(BaseModel):
    id: str
    label: str
    # Processo atualmente fazendo I/O neste disco (None se livre).
    activeIoProcess: ProcessCard | None = None
    # Processos que ja foram carregados na RAM a partir deste disco.
    inMemory: list[ProcessCard] = []
    # Processos que ainda estao so no armazenamento secundario (aguardando RAM).
    onDiskOnly: list[ProcessCard] = []


class EventEntry(BaseModel):
    id: str
    time: int
    message: str


class SimulatorSnapshot(BaseModel):
    clock: int
    cpus: list[CpuSlot]
    queues: list[QueueSnapshot]
    memory: MemorySnapshot
    disks: list[DiskSnapshot]
    eventLog: list[EventEntry]
    warnings: list[str] = []


class ProcessDescriptor(BaseModel):
    pid: str
    name: str
    process_class: str
    arrival_time: int = 0
    priority: int
    memory_mb: int
    cpu_burst_1: int
    io_disks: list[int] = []
    io_time: int = 0
    cpu_burst_2: int = 0
