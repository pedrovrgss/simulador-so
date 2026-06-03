from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProcessClass = Literal["tempo_real", "usuario"]


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class ProcessCard(ApiModel):
    pid: str
    name: str
    color: str
    class_label: str = Field(alias="classLabel")
    queue_label: str = Field(alias="queueLabel")


class CpuSlot(ApiModel):
    id: str
    label: str
    running_process: ProcessCard | None = Field(alias="runningProcess", default=None)
    quantum_left: int | None = Field(alias="quantumLeft", default=None)
    remaining_burst: int | None = Field(alias="remainingBurst", default=None)


class QueueSnapshot(ApiModel):
    id: str
    title: str
    kind: str
    processes: list[ProcessCard]


class MemoryBlock(ApiModel):
    id: str
    label: str
    occupied: bool
    owner_pid: str | None = Field(alias="ownerPid", default=None)
    color: str | None = None


class MemorySnapshot(ApiModel):
    total_mb: int = Field(alias="totalMb")
    used_mb: int = Field(alias="usedMb")
    blocks: list[MemoryBlock]


class DiskSnapshot(ApiModel):
    id: str
    label: str
    active_process: ProcessCard | None = Field(alias="activeProcess", default=None)
    waiting_queue: list[ProcessCard] = Field(alias="waitingQueue")


class EventEntry(ApiModel):
    id: str
    time: int
    message: str


class SimulatorSnapshot(ApiModel):
    clock: int
    cpus: list[CpuSlot]
    queues: list[QueueSnapshot]
    memory: MemorySnapshot
    disks: list[DiskSnapshot]
    event_log: list[EventEntry] = Field(alias="eventLog")


class ProcessDescriptor(ApiModel):
    pid: str
    name: str
    process_class: ProcessClass
    arrival_time: int
    priority: int
    memory_mb: int
    cpu_burst_1: int
    disk_id: int | None = None
    io_time: int | None = None
    cpu_burst_2: int | None = None
