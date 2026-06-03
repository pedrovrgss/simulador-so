from __future__ import annotations

from dataclasses import dataclass

from .models import ProcessDescriptor


class DescriptorFormatError(ValueError):
    """Erro para linhas invalidas do arquivo de entrada."""


@dataclass(frozen=True)
class ParsedInput:
    processes: list[ProcessDescriptor]
    warnings: list[str]


def parse_process_descriptors(content: str) -> ParsedInput:
    """
    Faz o parser de um formato inicial e simples de descritor.

    Formato esperado por linha:
    pid;nome;classe;chegada;prioridade;memoria_mb;cpu1;disco;io;cpu2

    Regras:
    - classe: TR ou U
    - disco, io e cpu2 podem ser "-"
    - processos de tempo real devem ter prioridade 0

    Este formato foi escolhido para iniciar o projeto e pode ser adaptado
    rapidamente quando o professor definir o layout final do arquivo.
    """

    processes: list[ProcessDescriptor] = []
    warnings: list[str] = []

    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        parts = [part.strip() for part in line.split(";")]
        if len(parts) != 10:
            raise DescriptorFormatError(
                f"Linha {line_number}: esperado 10 campos separados por ';'."
            )

        (
            pid,
            name,
            process_class_raw,
            arrival_time,
            priority,
            memory_mb,
            cpu_burst_1,
            disk_id,
            io_time,
            cpu_burst_2,
        ) = parts

        process_class = _parse_process_class(process_class_raw, line_number)
        priority_value = _parse_int(priority, "prioridade", line_number)
        memory_value = _parse_int(memory_mb, "memoria_mb", line_number)
        cpu1_value = _parse_int(cpu_burst_1, "cpu1", line_number)

        disk_value = _parse_optional_int(disk_id, "disco", line_number)
        io_value = _parse_optional_int(io_time, "io", line_number)
        cpu2_value = _parse_optional_int(cpu_burst_2, "cpu2", line_number)

        if process_class == "tempo_real":
            if priority_value != 0:
                raise DescriptorFormatError(
                    f"Linha {line_number}: processo de tempo real deve ter prioridade 0."
                )
            if memory_value > 512:
                warnings.append(
                    f"Linha {line_number}: processo {pid} excede 512 MB para tempo real."
                )

        descriptor = ProcessDescriptor(
            pid=pid,
            name=name,
            process_class=process_class,
            arrival_time=_parse_int(arrival_time, "chegada", line_number),
            priority=priority_value,
            memory_mb=memory_value,
            cpu_burst_1=cpu1_value,
            disk_id=disk_value,
            io_time=io_value,
            cpu_burst_2=cpu2_value,
        )
        processes.append(descriptor)

    return ParsedInput(processes=processes, warnings=warnings)


def _parse_process_class(value: str, line_number: int) -> str:
    normalized = value.upper()

    if normalized == "TR":
        return "tempo_real"
    if normalized == "U":
        return "usuario"

    raise DescriptorFormatError(
        f"Linha {line_number}: classe deve ser 'TR' ou 'U'."
    )


def _parse_int(raw: str, field_name: str, line_number: int) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        raise DescriptorFormatError(
            f"Linha {line_number}: campo '{field_name}' deve ser inteiro."
        ) from exc


def _parse_optional_int(raw: str, field_name: str, line_number: int) -> int | None:
    if raw == "-":
        return None

    return _parse_int(raw, field_name, line_number)
