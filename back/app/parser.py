from dataclasses import dataclass

from .models import ProcessDescriptor

# Leitura da entrada digitada na tela.
# O formato completo ajuda a testar TR e discos na apresentacao.


class DescriptorFormatError(ValueError):
    """Erro de entrada invalida."""


@dataclass
class ParsedInput:
    processes: list[ProcessDescriptor]
    warnings: list[str]


def parse_process_descriptors(content: str) -> ParsedInput:
    processes: list[ProcessDescriptor] = []
    warnings: list[str] = []
    # Guarda IDs que ja apareceram para nao aceitar processo repetido.
    seen_ids: list[str] = []

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        values = _split_descriptor(line, line_number)

        # Formato simples do enunciado. Por padrao vira processo de usuario.
        if len(values) == 5:
            pid, cpu1, io_time, cpu2, memory = values
            priority = 1
            disks = 0
        # Formato completo que usamos para demonstrar TR e uso de disco.
        elif len(values) == 7:
            pid, priority_raw, cpu1, io_time, cpu2, memory, disks_raw = values
            priority = _parse_int(priority_raw, "prioridade", line_number)
            disks = _parse_int(disks_raw, "discos", line_number)
        else:
            raise DescriptorFormatError(
                f"Linha {line_number}: use [id, cpu1, io, cpu2, ram] "
                "ou [id, prioridade, cpu1, io, cpu2, ram, discos]."
            )

        pid = pid.strip()
        # ID vazio ou repetido atrapalha memoria, filas e logs.
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
            cpu1_value,
            io_value,
            cpu2_value,
            memory_value,
            disks,
        )

        process_class = "tempo_real" if priority == 0 else "usuario"
        display_prefix = "TR" if priority == 0 else "U"

        processes.append(
            ProcessDescriptor(
                pid=pid,
                name=f"Processo {pid}",
                process_class=process_class,
                priority=priority,
                memory_mb=memory_value,
                cpu_burst_1=cpu1_value,
                io_time=io_value,
                cpu_burst_2=cpu2_value,
                disks_required=disks,
            )
        )

        if len(values) == 5:
            warnings.append(
                f"Linha {line_number}: {display_prefix}-{pid} entrou como usuario sem discos."
            )

    if not processes:
        raise DescriptorFormatError("Nenhum processo valido encontrado na entrada.")

    return ParsedInput(processes=processes, warnings=warnings)


def _split_descriptor(line: str, line_number: int) -> list[str]:
    # A entrada foi definida como lista entre colchetes, um processo por linha.
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


def _validate_descriptor(
    line_number: int,
    pid: str,
    priority: int,
    cpu1: int,
    io_time: int,
    cpu2: int,
    memory: int,
    disks: int,
) -> None:
    # As validacoes ficam juntas para o parser principal ficar mais facil de ler.
    if priority not in (0, 1):
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} deve ter prioridade 0 ou 1."
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

    if disks < 0 or disks > 4:
        raise DescriptorFormatError(
            f"Linha {line_number}: processo {pid} deve pedir entre 0 e 4 discos."
        )

    if io_time == 0 and cpu2 != 0:
        raise DescriptorFormatError(
            f"Linha {line_number}: CPU 2 deve ser 0 quando I/O for 0."
        )

    if priority == 0:
        # No trabalho, tempo real e simples: prioridade 0, pouca RAM e sem I/O.
        if memory > 512:
            raise DescriptorFormatError(
                f"Linha {line_number}: tempo real {pid} nao pode passar de 512 MiB."
            )
        if io_time != 0 or cpu2 != 0 or disks != 0:
            raise DescriptorFormatError(
                f"Linha {line_number}: tempo real {pid} nao usa I/O, CPU 2 ou discos."
            )
