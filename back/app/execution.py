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
        # Depois do I/O, a professora pediu para voltar na primeira fila.
        process.phase = "fase_cpu_2"
        process.queue_level = 0
        sim.log_event(
            f"{process.display_pid}: terminou I/O e voltou para a fila 1."
        )
        colocar_na_fila_pronto(sim, process)


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
    # Usuario com I/O sai da CPU e vai para a fila de bloqueados.
    if process.is_real_time or process.phase == "fase_cpu_2" or process.io_remaining == 0:
        finalizar_processo(sim, process)
        cpu.clear()
        return

    cpu.clear()
    process.phase = "fase_io"
    sim.change_state(process, "BLOQUEADO_IO")
    sim.blocked_io.append(process.pid)
    sim.log_event(
        f"{process.display_pid}: saiu da CPU e iniciou I/O por {process.io_remaining} u.t."
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
    # Finalizar tambem libera memoria e discos para processos que estavam esperando.
    sim.memory.free(process.display_pid)
    sim.disks.release(process.pid)
    sim.change_state(process, "FINALIZADO")

    if process.pid not in sim.finished:
        sim.finished.append(process.pid)

    sim.log_event(
        f"{process.display_pid}: finalizado. Memoria e discos liberados."
    )
