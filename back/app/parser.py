from dataclasses import dataclass

from .models import ProcessDescriptor
from .resources import TOTAL_DISKS

# Leitura da entrada digitada na tela.
# Formatos aceitos:
#   5 campos: [id, cpu1, io, cpu2, ram]
#   7 campos: [id, prioridade, cpu1, io, cpu2, ram, discos]          (legado, chegada=0)
#   8 campos: [id, prioridade, chegada, cpu1, io, cpu2, ram, discos] (completo)
#
# Campo "discos": IDs dos drives usados na fase de I/O, separados por espaco.
#   0       -> sem I/O de disco
#   1       -> usa apenas o drive 1
#   2 4     -> usa os drives 2 e 4 simultaneamente


class DescriptorFormatError(ValueError):
    """Erro de entrada invalida."""


@dataclass
class ParsedInput:
    processes: list[ProcessDescriptor]
    warnings: list[str]


def parse_process_descriptors(content: str) -> ParsedInput:
    processes: list[ProcessDescriptor] = []
    warnings: list[str] = []
    seen_ids: list[str] = []

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        values = _split_descriptor(line, line_number)

        if len(values) == 5:
            pid, cpu1, io_time, cpu2, memory = values
            priority = 1
            disks: list[int] = []
            arrival = 0
        elif len(values) == 7:
            # Formato legado sem campo de chegada; assume chegada no t=0.
            pid, priority_raw, cpu1, io_time, cpu2, memory, disks_raw = values
            priority = _parse_int(priority_raw, "prioridade", line_number)
            disks = _parse_disk_ids(disks_raw, line_number)
            arrival = 0
        elif len(values) == 8:
            pid, priority_raw, arrival_raw, cpu1, io_time, cpu2, memory, disks_raw = values
            priority = _parse_int(priority_raw, "prioridade", line_number)
            disks = _parse_disk_ids(disks_raw, line_number)
            arrival = _parse_int(arrival_raw, "chegada", line_number)
        else:
            raise DescriptorFormatError(
                f"Linha {line_number}: use [id, cpu1, io, cpu2, ram], "
                "[id, prioridade, cpu1, io, cpu2, ram, discos] "
                "ou [id, prioridade, chegada, cpu1, io, cpu2, ram, discos]."
            )

        pid = pid.strip()
        if not pid:
            raise DescriptorFormatError(f"Linha {line_number}: id vazio.")
        if pid in seen_ids:
            raise DescriptorFormatError(f"Linha {line_number}: id {pid} repetido.")
        seen_ids.append(pid)

        cpu1_value = _parse_int(cpu1, "cpu1", line_number)
        io_value = _parse_int(io_time, "io", line_number)
        cpu2_value = _parse_int(cpu2, "cpu2", line_number)
        memory_value = _parse_int(memory, "ram", line_number)

        _validate_descriptor(
            line_number,
            pid,
            priority,
            arrival,
            cpu1_value,
            io_value,
            cpu2_value,
            memory_value,
            disks,
        )

        process_class = "tempo_real" if priority == 0 else "usuario"
        # TR = tempo real (priority 0); IO = usuario (priority 1).
        display_prefix = "TR" if priority == 0 else "IO"

        processes.append(
            ProcessDescriptor(
                pid=pid,
                name=f"Processo {pid}",
                process_class=process_class,
                arrival_time=arrival,
                priority=priority,
                memory_mb=memory_value,
                cpu_burst_1=cpu1_value,
                io_time=io_value,
                cpu_burst_2=cpu2_value,
                io_disks=disks,
            )
        )

        if len(values) == 5:
            warnings.append(
                f"Linha {line_number}: {display_prefix}-{pid} entrou como usuario sem discos."
            )

    if not processes:
        raise DescriptorFormatError("Nenhum processo valido encontrado na entrada.")

    # Aviso se dois processos tiverem o mesmo tempo de chegada.
    # Cada tick e uma unidade de clock; dois processos nao podem chegar no mesmo instante.
    seen_arrivals: dict[int, str] = {}
    for p in processes:
        if p.arrival_time in seen_arrivals:
            warnings.append(
                f"Processos {seen_arrivals[p.arrival_time]} e {p.pid} chegam no mesmo tick "
                f"({p.arrival_time}). Em um clock real cada chegada ocupa um ciclo distinto."
            )
        else:
            seen_arrivals[p.arrival_time] = p.pid

    return ParsedInput(processes=processes, warnings=warnings)


def _split_descriptor(line: str, line_number: int) -> list[str]:
    if not (line.startswith("[") and line.endswith("]")):
        raise DescriptorFormatError(
            f"Linha {line_number}: descritor deve estar entre colchetes."
        )

    body = line[1:-1].strip()
    if not body:
        raise DescriptorFormatError(f"Linha {line_number}: descritor vazio.")

    values: list[str] = []
    for part in body.split(","):
        values.append(part.strip())

    return values


def _parse_int(raw: str, field_name: str, line_number: int) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise DescriptorFormatError(
            f"Linha {line_number}: campo '{field_name}' deve ser inteiro."
        ) from exc


def _parse_disk_ids(raw: str, line_number: int) -> list[int]:
    """Converte '0', '2', '1 3' etc. na lista de IDs de drive [2], [1, 3], etc."""
    parts = raw.split()
    if len(parts) == 1 and parts[0] == "0":
        return []
    ids: list[int] = []
    for part in parts:
        try:
            disk_id = int(part)
        except ValueError as exc:
            raise DescriptorFormatError(
                f"Linha {line_number}: campo 'discos' deve conter IDs de drive (ex: '1', '2 4')."
            ) from exc
        ids.append(disk_id)
    return ids


def _validate_descriptor(
    line_number: int,
    pid: str,
    priority: int,
    arrival: int,
    cpu1: int,
    io_time: int,
    cpu2: int,
    memory: int,
    disks: list[int],
) -> None:
    if priority not in (0, 1):
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} deve ter prioridade 0 ou 1."
        )

    if arrival < 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} nao pode ter tempo de chegada negativo."
        )

    if cpu1 < 0 or io_time < 0 or cpu2 < 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: duracoes de CPU e I/O nao podem ser negativas."
        )

    if cpu1 == 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} precisa ter CPU 1 maior que zero."
        )

    if memory <= 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} deve ter RAM positiva."
        )

    for d in disks:
        if d < 1 or d > TOTAL_DISKS:
            raise DescriptorFormatError(
                f"Linha {line_number}: processo {pid} referencia drive {d} invalido (1-{TOTAL_DISKS})."
            )
    if len(disks) != len(set(disks)):
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} repete IDs de drive."
        )
    if len(disks) > TOTAL_DISKS:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} solicita mais drives do que existem."
        )

    if io_time == 0 and cpu2 != 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: CPU 2 deve ser 0 quando I/O for 0."
        )

    if io_time == 0 and disks:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} sem I/O nao pode declarar drives."
        )

    if priority == 0:
        if memory > 512:
            raise DescriptorFormatError(
                f"Linha {line_number}: tempo real {pid} nao pode passar de 512 MiB."
            )
        if io_time != 0 or cpu2 != 0 or disks:
            raise DescriptorFormatError(
                f"Linha {line_number}: tempo real {pid} nao usa I/O, CPU 2 ou discos."
            )
