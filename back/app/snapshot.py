from .memory import MemoryManager
from .models import CpuSlot, DiskSnapshot, EventEntry, ProcessCard, QueueSnapshot, SimulatorSnapshot
from .resources import DiskManager
from .runtime import CpuRuntime, ProcessRuntime
from .scheduler import Scheduler

# Adaptacao do estado interno para o formato que o frontend desenha.
# Separar isso evita misturar regra da simulacao com layout da tela.


def build_snapshot(
    *,
    clock: int,
    cpus: list[CpuRuntime],
    processes: dict[str, ProcessRuntime],
    scheduler: Scheduler,
    memory: MemoryManager,
    disks: DiskManager,
    blocked_io: list[str],
    blocked_disk: list[str],
    waiting_memory: list[str],
    waiting_dma_memory: list[str],
    loading_memory: list[str],
    finished: list[str],
    rejected: list[str],
    events: list[EventEntry],
    warnings: list[str],
) -> SimulatorSnapshot:
    cards = _process_cards(processes, blocked_disk)

    # Processos em loading_memory tiveram RAM reservada mas o DMA ainda nao concluiu.
    loading_display_pids = frozenset(
        processes[pid].display_pid
        for pid in loading_memory
        if pid in processes
    )

    return SimulatorSnapshot(
        clock=clock,
        cpus=_cpu_snapshots(cpus, processes, cards),
        queues=_queue_snapshots(
            scheduler=scheduler,
            cards=cards,
            blocked_io=blocked_io,
            blocked_disk=blocked_disk,
            waiting_memory=waiting_memory,
            waiting_dma_memory=waiting_dma_memory,
            loading_memory=loading_memory,
            finished=finished,
            rejected=rejected,
        ),
        memory=memory.to_snapshot(hidden_pids=loading_display_pids),
        disks=_disk_snapshots(
            processes=processes,
            cards=cards,
            disks=disks,
            waiting_memory=waiting_memory,
            waiting_dma_memory=waiting_dma_memory,
            loading_memory=loading_memory,
            finished=finished,
            rejected=rejected,
        ),
        eventLog=events[-200:],
        warnings=warnings,
    )


def _process_cards(
    processes: dict[str, ProcessRuntime],
    blocked_disk: list[str],
) -> dict[str, ProcessCard]:
    blocked_disk_set = set(blocked_disk)
    cards: dict[str, ProcessCard] = {}

    for pid, process in processes.items():
        cards[pid] = ProcessCard(
            pid=process.display_pid,
            name=process.descriptor.name,
            color=process.color,
            classLabel="Tempo real" if process.is_real_time else (
                "CPU Bound" if process.descriptor.io_time == 0 else "I/O Bound"
            ),
            queueLabel=_queue_label(process, blocked_disk_set),
            memoryMb=process.memory_mb,
        )

    return cards


def _cpu_snapshots(
    cpus: list[CpuRuntime],
    processes: dict[str, ProcessRuntime],
    cards: dict[str, ProcessCard],
) -> list[CpuSlot]:
    snapshots: list[CpuSlot] = []

    for cpu in cpus:
        process = processes[cpu.pid] if cpu.pid else None
        snapshots.append(
            CpuSlot(
                id=f"cpu-{cpu.id}",
                label=f"CPU {cpu.id}",
                runningProcess=cards[process.pid] if process else None,
                quantumLeft=cpu.quantum_left,
                remainingBurst=process.current_cpu_remaining() if process else None,
                totalBurst=process.total_for_current_phase() if process else None,
                phase=process.phase if process else None,
            )
        )

    return snapshots


def _disk_snapshots(
    *,
    processes: dict[str, ProcessRuntime],
    cards: dict[str, ProcessCard],
    disks: DiskManager,
    waiting_memory: list[str],
    waiting_dma_memory: list[str],
    loading_memory: list[str],
    finished: list[str],
    rejected: list[str],
) -> list[DiskSnapshot]:
    inactive = set(finished) | set(rejected)
    # "somente em disco": aguardando RAM, aguardando canal DMA ou em transferencia DMA.
    on_disk_only = set(waiting_memory) | set(waiting_dma_memory) | set(loading_memory)

    by_disk: dict[int, list[str]] = {i: [] for i in range(1, 5)}
    for pid, process in processes.items():
        if pid not in inactive:
            by_disk[process.home_disk_id].append(pid)

    snapshots: list[DiskSnapshot] = []
    for disk_id in range(1, 5):
        active_io_pid = disks.active_io_pid(disk_id)
        active_card = cards.get(active_io_pid) if active_io_pid else None

        in_memory: list[ProcessCard] = []
        on_disk: list[ProcessCard] = []

        for pid in by_disk[disk_id]:
            card = cards.get(pid)
            if card is None:
                continue
            if pid in on_disk_only:
                on_disk.append(card)
            else:
                in_memory.append(card)

        snapshots.append(DiskSnapshot(
            id=f"disk-{disk_id}",
            label=f"Disco {disk_id}",
            activeIoProcess=active_card,
            inMemory=in_memory,
            onDiskOnly=on_disk,
        ))

    return snapshots


def _queue_snapshots(
    *,
    scheduler: Scheduler,
    cards: dict[str, ProcessCard],
    blocked_io: list[str],
    blocked_disk: list[str],
    waiting_memory: list[str],
    waiting_dma_memory: list[str],
    loading_memory: list[str],
    finished: list[str],
    rejected: list[str],
) -> list[QueueSnapshot]:
    queues = scheduler.queue_items()

    # Fila de memoria: em DMA ativo | aguardando canal DMA | aguardando RAM.
    fila_memoria_pids = loading_memory + waiting_dma_memory + list(waiting_memory)

    # Fila de I/O: processos aguardando disco primeiro, depois os em transferencia ativa.
    # Os em blocked_io tem drives adquiridos; os em blocked_disk ainda aguardam o drive.
    fila_io_pids = blocked_disk + blocked_io

    return [
        _queue("fila-tr", "FCFS", "FCFS", queues["FCFS"], cards),
        _queue("fila-f1", "Fila de feedback 1", "Nivel 1", queues["U0"], cards),
        _queue("fila-f2", "Fila de feedback 2", "Nivel 2", queues["U1"], cards),
        _queue("fila-f3", "Fila de feedback 3", "Nivel 3", queues["U2"], cards),
        _queue(
            "fila-dma",
            "Aguardando I/O",
            "DMA",
            fila_io_pids,
            cards,
            active_pids=blocked_io,
        ),
        _queue(
            "fila-memoria",
            "Aguardando memoria",
            "Carga DMA",
            fila_memoria_pids,
            cards,
            active_pids=loading_memory[:1],
        ),
        _queue("fila-finalizados", "Finalizados", "Concluidos", finished, cards),
        _queue("fila-rejeitados", "Rejeitados", "Invalidos", rejected, cards),
    ]


def _queue(
    queue_id: str,
    title: str,
    kind: str,
    pids: list[str],
    cards: dict[str, ProcessCard],
    active_pids: list[str] | None = None,
) -> QueueSnapshot:
    active_process_pids = None
    if active_pids is not None:
        active_process_pids = [cards[pid].pid for pid in active_pids if pid in cards]

    return QueueSnapshot(
        id=queue_id,
        title=title,
        kind=kind,
        processes=_cards_from_pids(pids, cards),
        activeProcessPids=active_process_pids,
    )


def _queue_label(process: ProcessRuntime, blocked_disk_set: set[str]) -> str:
    if process.state == "FINALIZADO":
        return "Finalizado"
    if process.state == "BLOQUEADO_IO":
        if process.io_disks:
            return "Disco " + " e ".join(str(d) for d in process.io_disks)
        return "I/O"
    if process.pid in blocked_disk_set:
        return "Aguardando disco"
    if process.is_real_time:
        return "FCFS"
    return f"Feedback {process.queue_level + 1}"


def _cards_from_pids(
    pids: list[str],
    cards: dict[str, ProcessCard],
) -> list[ProcessCard]:
    return [cards[pid] for pid in pids if pid in cards]
