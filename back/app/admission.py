from .memory import MEMORIA_TOTAL_MIB
from .models import ProcessDescriptor
from .parser import ParsedInput
from .runtime import ProcessRuntime
from .sample_data import PROCESS_COLORS
from .scheduler import nome_fila

# Entrada dos processos no sistema.
# Fluxo de admissao: disco primeiro, memoria depois.
# Os processos existem em armazenamento secundario e chegam ao sistema
# conforme seus tempos de chegada, sendo carregados na RAM via DMA.


def preparar_processos(sim, parsed: ParsedInput) -> None:
    """Registra os processos com seus tempos de chegada sem admiti-los ainda."""
    sim.pending_processes = list(enumerate(parsed.processes))


def admitir_chegadas(sim) -> None:
    """Admite os processos cujo tempo de chegada e igual ao clock atual."""
    chegaram = [
        (index, descriptor)
        for index, descriptor in sim.pending_processes
        if descriptor.arrival_time == sim.clock
    ]

    for index, descriptor in chegaram:
        sim.pending_processes.remove((index, descriptor))

        process = ProcessRuntime(
            descriptor=descriptor,
            pid=descriptor.pid,
            display_pid=montar_pid_visual(descriptor),
            color=PROCESS_COLORS[index % len(PROCESS_COLORS)],
            priority=descriptor.priority,
            memory_mb=descriptor.memory_mb,
            io_disks=descriptor.io_disks,
            is_real_time=descriptor.priority == 0,
            cpu1_remaining=descriptor.cpu_burst_1,
            io_remaining=descriptor.io_time,
            cpu2_remaining=descriptor.cpu_burst_2,
            # Todos os processos residem em algum disco secundario.
            # Distribuicao round-robin entre os 4 drives para exibicao.
            home_disk_id=(index % 4) + 1,
        )

        # Processos sem I/O (TR-nnn) usam a fase cpu_bound independente de prioridade.
        # Processos com I/O (IO-nnn) ficam com o default fase_cpu_1 e avancam para fase_cpu_2.
        if descriptor.io_time == 0:
            process.phase = "cpu_bound"

        sim.processes[process.pid] = process
        sim.log_event(f"{process.display_pid}: chegou ao sistema (Disco {process.home_disk_id}).")
        admitir_processo(sim, process)


def admitir_processo(sim, process: ProcessRuntime) -> None:
    if process.memory_mb > MEMORIA_TOTAL_MIB:
        sim.change_state(process, "REJEITADO")
        sim.rejected.append(process.pid)
        sim.log_event(
            f"{process.display_pid}: rejeitado porque pede mais RAM que o total."
        )
        return

    _carregar_na_memoria(sim, process)


def _carregar_na_memoria(sim, process: ProcessRuntime) -> None:
    if not sim.memory.allocate(process.display_pid, process.memory_mb, process.color):
        sim.change_state(process, "ESPERANDO_MEMORIA")
        sim.waiting_memory.append(process.pid)
        sim.log_event(f"{process.display_pid}: aguardando memoria livre.")
        return

    _iniciar_dma_memoria(sim, process)


def _iniciar_dma_memoria(sim, process: ProcessRuntime) -> None:
    """Tenta iniciar o carregamento DMA disco->RAM.
    Se nao houver canal DMA livre, o processo entra em waiting_dma_memory."""
    if sim.dma.available():
        sim.dma.acquire(process.pid)
        sim.loading_memory.append(process.pid)
        sim.log_event(
            f"{process.display_pid}: iniciando DMA disco->RAM ({process.memory_mb} MiB)."
        )
    else:
        sim.waiting_dma_memory.append(process.pid)
        sim.log_event(f"{process.display_pid}: aguardando canal DMA livre.")


def avancar_carregamento_memoria(sim) -> None:
    """Conclui o DMA de todos os processos que iniciaram no tick anterior e
    tenta iniciar DMA para os que estavam aguardando canal."""
    for pid in list(sim.loading_memory):
        sim.loading_memory.remove(pid)
        sim.dma.release(pid)
        process = sim.processes[pid]
        sim.log_event(f"{process.display_pid}: DMA concluido; pronto para executar.")
        colocar_na_fila_pronto(sim, process)
    tentar_dma_memoria(sim)


def tentar_dma_memoria(sim) -> None:
    """Atribui canais DMA livres aos processos em waiting_dma_memory."""
    for pid in list(sim.waiting_dma_memory):
        if not sim.dma.available():
            break
        sim.waiting_dma_memory.remove(pid)
        sim.dma.acquire(pid)
        sim.loading_memory.append(pid)
        process = sim.processes[pid]
        sim.log_event(
            f"{process.display_pid}: canal DMA livre; iniciando DMA disco->RAM ({process.memory_mb} MiB)."
        )


def tentar_processos_em_espera(sim) -> None:
    for pid in list(sim.waiting_memory):
        process = sim.processes[pid]
        if sim.memory.allocate(process.display_pid, process.memory_mb, process.color):
            sim.waiting_memory.remove(pid)
            _iniciar_dma_memoria(sim, process)


def colocar_na_fila_pronto(sim, process: ProcessRuntime) -> None:
    sim.change_state(process, "PRONTO")
    queue_name = sim.scheduler.add_ready(
        process.pid,
        process.priority,
        process.queue_level,
    )
    sim.log_event(f"{process.display_pid}: entrou na {nome_fila(queue_name)}.")


def montar_pid_visual(descriptor: ProcessDescriptor) -> str:
    raw_pid = descriptor.pid
    normalized = raw_pid.upper()

    if normalized.startswith("TR-") or normalized.startswith("IO-"):
        return raw_pid

    # TR = tempo real (priority 0, FCFS); IO = usuario (priority 1, feedback).
    prefix = "TR" if descriptor.priority == 0 else "IO"
    if raw_pid.isdigit():
        return f"{prefix}-{int(raw_pid):02d}"

    return f"{prefix}-{raw_pid}"
