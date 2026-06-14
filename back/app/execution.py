from .admission import colocar_na_fila_pronto
from .runtime import CpuRuntime, ProcessRuntime
from .scheduler import QUANTUM_USUARIO, nome_fila

# Regras que acontecem a cada unidade de tempo:
# CPU anda, I/O anda, quantum acaba e processo finaliza.


def despachar_cpus_livres(sim) -> None:
    for cpu in sim.cpus:
        if cpu.pid is not None:
            continue

        # O escalonador decide a proxima fila; aqui so colocamos na CPU livre.
        next_item = sim.scheduler.next_process()
        if next_item is None:
            continue

        pid, queue_name = next_item
        process = sim.processes[pid]

        cpu.pid = pid
        # Tempo real nao sofre preempcao por quantum; usuario recebe quantum 2.
        cpu.quantum_left = None if process.is_real_time else QUANTUM_USUARIO
        sim.change_state(process, "EXECUTANDO")
        sim.log_event(
            f"CPU {cpu.id}: iniciou {process.display_pid} pela {nome_fila(queue_name)}."
        )


def avancar_io(sim) -> None:
    # Copiamos a lista porque ela pode ser alterada dentro do proprio loop.
    for pid in list(sim.blocked_io):
        process = sim.processes[pid]
        process.io_remaining -= 1

        if process.io_remaining > 0:
            continue

        sim.blocked_io.remove(pid)
        sim.disks.release_io(pid)
        # Depois do I/O, a professora pediu para voltar na primeira fila.
        process.phase = "fase_cpu_2"
        process.queue_level = 0
        sim.log_event(
            f"{process.display_pid}: terminou I/O e voltou para a fila 1."
        )
        colocar_na_fila_pronto(sim, process)

    # Verifica se algum processo bloqueado por disco pode agora iniciar o I/O.
    _tentar_bloqueados_disco(sim)


def avancar_cpus(sim) -> None:
    for cpu in sim.cpus:
        if cpu.pid is None:
            continue

        process = sim.processes[cpu.pid]
        process.decrease_cpu()

        if cpu.quantum_left is not None:
            cpu.quantum_left -= 1

        # Final da fase de CPU tem prioridade sobre preempcao por quantum.
        if process.current_cpu_remaining() == 0:
            tratar_fim_da_fase_cpu(sim, cpu, process)
        elif cpu.quantum_left == 0:
            preemptar_usuario(sim, cpu, process)


def tratar_fim_da_fase_cpu(
    sim,
    cpu: CpuRuntime,
    process: ProcessRuntime,
) -> None:
    # TR e processo sem I/O terminam direto ao acabar a CPU atual.
    # Usuario com I/O sai da CPU e vai para a fila de bloqueados (com ou sem disco livre).
    if process.is_real_time or process.phase == "fase_cpu_2" or process.io_remaining == 0:
        finalizar_processo(sim, process)
        cpu.clear()
        return

    cpu.clear()
    process.phase = "fase_io"

    if sim.disks.can_acquire(process.io_disks):
        # Drives livres: inicia I/O imediatamente.
        sim.disks.acquire_io(process.pid, process.io_disks)
        sim.change_state(process, "BLOQUEADO_IO")
        sim.blocked_io.append(process.pid)
        disks_str = _format_disks(process.io_disks)
        sim.log_event(
            f"{process.display_pid}: saiu da CPU e iniciou I/O{disks_str} por {process.io_remaining} u.t."
        )
    else:
        # Drives ocupados: aguarda na fila de bloqueados por disco.
        sim.change_state(process, "ESPERANDO_DISCO")
        sim.blocked_disk.append(process.pid)
        disks_str = _format_disks(process.io_disks)
        sim.log_event(
            f"{process.display_pid}: saiu da CPU; aguardando disco{disks_str} livre."
        )


def preemptar_usuario(
    sim,
    cpu: CpuRuntime,
    process: ProcessRuntime,
) -> None:
    old_level = process.queue_level
    # U0, U1 e U2 representam as filas 1, 2 e 3 do feedback.
    # Na ultima fila, se o quantum acabar, o processo volta para a primeira.
    if process.queue_level == 2:
        process.queue_level = 0
    else:
        process.queue_level += 1

    cpu.clear()
    sim.change_state(process, "PRONTO")
    sim.scheduler.add_ready(process.pid, process.priority, process.queue_level)

    if old_level == 2:
        sim.log_event(
            f"{process.display_pid}: quantum acabou na fila 3; voltou para a fila 1."
        )
    else:
        old_queue = old_level + 1
        new_queue = process.queue_level + 1
        sim.log_event(
            f"{process.display_pid}: quantum acabou; saiu da fila {old_queue} e foi para a fila {new_queue}."
        )


def finalizar_processo(sim, process: ProcessRuntime) -> None:
    # Finalizar libera memoria e drives de I/O (caso o processo tenha terminado durante I/O).
    sim.memory.free(process.display_pid)
    sim.disks.release_io(process.pid)
    sim.change_state(process, "FINALIZADO")

    if process.pid not in sim.finished:
        sim.finished.append(process.pid)

    sim.log_event(
        f"{process.display_pid}: finalizado. Memoria liberada."
    )

    # Liberar drives pode desbloquear processos aguardando disco.
    _tentar_bloqueados_disco(sim)


def _tentar_bloqueados_disco(sim) -> None:
    """Tenta iniciar I/O nos processos que estavam esperando drives livres."""
    for pid in list(sim.blocked_disk):
        process = sim.processes[pid]
        if sim.disks.can_acquire(process.io_disks):
            sim.disks.acquire_io(pid, process.io_disks)
            sim.blocked_disk.remove(pid)
            sim.blocked_io.append(pid)
            sim.change_state(process, "BLOQUEADO_IO")
            disks_str = _format_disks(process.io_disks)
            sim.log_event(
                f"{process.display_pid}: disco{disks_str} livre; iniciou I/O por {process.io_remaining} u.t."
            )


def _format_disks(disk_ids: list[int]) -> str:
    if not disk_ids:
        return ""
    ids = " e ".join(str(d) for d in disk_ids)
    return f" (Disco {ids})"
