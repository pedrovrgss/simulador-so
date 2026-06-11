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
    label: str
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
    status: str
    ownerProcess: ProcessCard | None = None
    activeProcess: ProcessCard | None = None
    waitingQueue: list[ProcessCard]


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


class ProcessDescriptor(BaseModel):
    pid: str
    name: str
    process_class: str
    arrival_time: int = 0
    priority: int
    memory_mb: int
    cpu_burst_1: int
    disks_required: int = 0
    io_time: int = 0
    cpu_burst_2: int = 0
