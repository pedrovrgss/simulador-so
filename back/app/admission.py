from .memory import MEMORIA_TOTAL_MIB
from .models import ProcessDescriptor
from .parser import ParsedInput
from .runtime import ProcessRuntime
from .sample_data import PROCESS_COLORS
from .scheduler import nome_fila

# Entrada dos processos no sistema.
# Primeiro tentamos memoria, depois disco, e por ultimo fila de pronto.


def criar_processos(sim, parsed: ParsedInput) -> None:
    for index, descriptor in enumerate(parsed.processes):
        # ProcessRuntime e a copia "viva" do processo durante a simulacao.
        process = ProcessRuntime(
            descriptor=descriptor,
            pid=descriptor.pid,
            display_pid=montar_pid_visual(descriptor),
            color=PROCESS_COLORS[index % len(PROCESS_COLORS)],
            priority=descriptor.priority,
            memory_mb=descriptor.memory_mb,
            disks_required=descriptor.disks_required,
            is_real_time=descriptor.priority == 0,
            cpu1_remaining=descriptor.cpu_burst_1,
            io_remaining=descriptor.io_time,
            cpu2_remaining=descriptor.cpu_burst_2,
        )

        if descriptor.io_time == 0 and descriptor.priority == 1:
            # Usuario sem I/O nao passa pela fase de disco; ele e CPU-bound.
            process.phase = "cpu_bound"

        sim.processes[process.pid] = process
        sim.log_event(f"{process.display_pid}: processo criado.")
        admitir_processo(sim, process)


def admitir_processo(sim, process: ProcessRuntime) -> None:
    # Processo maior que a memoria total nunca vai conseguir entrar.
    if process.memory_mb > MEMORIA_TOTAL_MIB:
        sim.change_state(process, "REJEITADO")
        sim.rejected.append(process.pid)
        sim.log_event(
            f"{process.display_pid}: rejeitado porque pede mais RAM que o total."
        )
        return

    # Se nao couber agora, fica esperando ate outro processo liberar memoria.
    if not sim.memory.allocate(process.display_pid, process.memory_mb, process.color):
        sim.change_state(process, "ESPERANDO_MEMORIA")
        sim.waiting_memory.append(process.pid)
        sim.log_event(f"{process.display_pid}: aguardando memoria livre.")
        return

    sim.log_event(
        f"{process.display_pid}: entrou na memoria ({process.memory_mb} MiB)."
    )
    reservar_disco_ou_esperar(sim, process)


def reservar_disco_ou_esperar(sim, process: ProcessRuntime) -> None:
    # A reserva acontece antes da fila de pronto para evitar iniciar sem recurso.
    if sim.disks.reserve(process.pid, process.disks_required):
        if process.disks_required > 0:
            sim.log_event(
                f"{process.display_pid}: reservou {process.disks_required} disco(s)."
            )
        colocar_na_fila_pronto(sim, process)
        return

    sim.change_state(process, "ESPERANDO_RECURSO")
    if process.pid not in sim.waiting_resource:
        sim.waiting_resource.append(process.pid)
    sim.log_event(f"{process.display_pid}: aguardando disco livre.")


def tentar_processos_em_espera(sim) -> None:
    # Depois que algum recurso libera, tentamos acordar quem ficou esperando.
    for pid in list(sim.waiting_memory):
        process = sim.processes[pid]
        if sim.memory.allocate(process.display_pid, process.memory_mb, process.color):
            sim.waiting_memory.remove(pid)
            sim.log_event(
                f"{process.display_pid}: conseguiu memoria e saiu da espera."
            )
            reservar_disco_ou_esperar(sim, process)

    for pid in list(sim.waiting_resource):
        process = sim.processes[pid]
        if sim.disks.reserve(process.pid, process.disks_required):
            sim.waiting_resource.remove(pid)
            sim.log_event(f"{process.display_pid}: conseguiu disco livre.")
            colocar_na_fila_pronto(sim, process)


def colocar_na_fila_pronto(sim, process: ProcessRuntime) -> None:
    # Depois que tem memoria e recurso, o escalonador pode escolher o processo.
    sim.change_state(process, "PRONTO")
    queue_name = sim.scheduler.add_ready(
        process.pid,
        process.priority,
        process.queue_level,
    )
    sim.log_event(f"{process.display_pid}: entrou na {nome_fila(queue_name)}.")


def montar_pid_visual(descriptor: ProcessDescriptor) -> str:
    # Mantem IDs ja formatados, mas transforma "1" em "TR-01" ou "U-01".
    raw_pid = descriptor.pid
    normalized = raw_pid.upper()

    if normalized.startswith("TR-") or normalized.startswith("U-"):
        return raw_pid

    prefix = "TR" if descriptor.priority == 0 else "U"
    if raw_pid.isdigit():
        return f"{prefix}-{int(raw_pid):02d}"

    return f"{prefix}-{raw_pid}"
