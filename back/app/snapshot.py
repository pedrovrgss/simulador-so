from .memory import MemoryManager
from .models import CpuSlot, EventEntry, ProcessCard, QueueSnapshot, SimulatorSnapshot
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
    waiting_memory: list[str],
    finished: list[str],
    rejected: list[str],
    events: list[EventEntry],
) -> SimulatorSnapshot:
    # Primeiro criamos um card por processo para reaproveitar em CPU, filas e disco.
    cards = _process_cards(processes, disks)

    return SimulatorSnapshot(
        clock=clock,
        cpus=_cpu_snapshots(cpus, processes, cards),
        queues=_queue_snapshots(
            scheduler=scheduler,
            cards=cards,
            blocked_io=blocked_io,
            waiting_memory=waiting_memory,
            finished=finished,
            rejected=rejected,
        ),
        memory=memory.to_snapshot(),
        disks=disks.to_snapshot(
            process_cards=cards,
            active_io_pids=blocked_io,
        ),
        eventLog=events[-200:],
    )


def _process_cards(
    processes: dict[str, ProcessRuntime],
    disks: DiskManager,
) -> dict[str, ProcessCard]:
    cards: dict[str, ProcessCard] = {}

    for pid, process in processes.items():
        # O card e a versao resumida do processo que o frontend consegue desenhar.
        cards[pid] = ProcessCard(
            pid=process.display_pid,
            name=process.descriptor.name,
            color=process.color,
            classLabel="Tempo real" if process.is_real_time else "Usuario",
            queueLabel=_queue_label(process, disks),
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
        # Se a CPU estiver livre, enviamos None para o frontend mostrar "sem processo".
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


def _queue_snapshots(
    *,
    scheduler: Scheduler,
    cards: dict[str, ProcessCard],
    blocked_io: list[str],
    waiting_memory: list[str],
    finished: list[str],
    rejected: list[str],
) -> list[QueueSnapshot]:
    queues = scheduler.queue_items()

    # Os IDs das filas precisam bater com os nomes usados nos componentes do front.
    return [
        _queue("fila-tr", "FCFS", "FCFS", queues["FCFS"], cards),
        _queue("fila-f1", "Fila de feedback 1", "Nivel 1", queues["U0"], cards),
        _queue("fila-f2", "Fila de feedback 2", "Nivel 2", queues["U1"], cards),
        _queue("fila-f3", "Fila de feedback 3", "Nivel 3", queues["U2"], cards),
        _queue(
            "fila-dma",
            "Aguardando I/O",
            "DMA",
            blocked_io,
            cards,
            active_pids=blocked_io[:1],
        ),
        _queue("fila-memoria", "Aguardando memoria", "First Fit", waiting_memory, cards),
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
        # Na fila de I/O, o primeiro bloqueado aparece como processo ativo.
        active_process_pids = []
        for pid in active_pids:
            if pid in cards:
                active_process_pids.append(cards[pid].pid)

    return QueueSnapshot(
        id=queue_id,
        title=title,
        kind=kind,
        processes=_cards_from_pids(pids, cards),
        activeProcessPids=active_process_pids,
    )


def _queue_label(process: ProcessRuntime, disks: DiskManager) -> str:
    # Label pequeno que aparece dentro do card do processo na tela.
    if process.state == "FINALIZADO":
        return "Finalizado"
    if process.state == "BLOQUEADO_IO":
        disk_ids = disks.owners_disks(process.pid)
        return f"Disco {disk_ids[0]}" if disk_ids else "I/O"
    if process.is_real_time:
        return "FCFS"
    return f"Feedback {process.queue_level + 1}"


def _cards_from_pids(
    pids: list[str],
    cards: dict[str, ProcessCard],
) -> list[ProcessCard]:
    result: list[ProcessCard] = []

    for pid in pids:
        if pid in cards:
            result.append(cards[pid])

    return result
