from __future__ import annotations

from .models import SimulatorSnapshot


def build_sample_snapshot() -> SimulatorSnapshot:
    return SimulatorSnapshot.model_validate(
        {
            "clock": 18,
            "cpus": [
                {
                    "id": "cpu-1",
                    "label": "CPU 1",
                    "runningProcess": {
                        "pid": "TR-01",
                        "name": "Controle de voo",
                        "color": "#ff6b57",
                        "classLabel": "Tempo real",
                        "queueLabel": "FCFS",
                    },
                    "quantumLeft": None,
                    "remainingBurst": 4,
                },
                {
                    "id": "cpu-2",
                    "label": "CPU 2",
                    "runningProcess": {
                        "pid": "U-07",
                        "name": "Editor",
                        "color": "#42d392",
                        "classLabel": "Usuario",
                        "queueLabel": "Feedback 1",
                    },
                    "quantumLeft": 1,
                    "remainingBurst": 2,
                },
                {
                    "id": "cpu-3",
                    "label": "CPU 3",
                    "runningProcess": {
                        "pid": "U-03",
                        "name": "Compilador",
                        "color": "#5cc8ff",
                        "classLabel": "Usuario",
                        "queueLabel": "Feedback 2",
                    },
                    "quantumLeft": 2,
                    "remainingBurst": 5,
                },
                {
                    "id": "cpu-4",
                    "label": "CPU 4",
                    "runningProcess": None,
                    "quantumLeft": None,
                    "remainingBurst": None,
                },
            ],
            "queues": [
                {
                    "id": "fila-tr",
                    "title": "Fila de tempo real",
                    "kind": "FCFS",
                    "processes": [
                        {
                            "pid": "TR-02",
                            "name": "Monitoramento",
                            "color": "#f59e0b",
                            "classLabel": "Tempo real",
                            "queueLabel": "FCFS",
                        }
                    ],
                },
                {
                    "id": "fila-f1",
                    "title": "Fila de feedback 1",
                    "kind": "Alta prioridade",
                    "processes": [
                        {
                            "pid": "U-11",
                            "name": "Planilhas",
                            "color": "#7dd3fc",
                            "classLabel": "Usuario",
                            "queueLabel": "Feedback 1",
                        },
                        {
                            "pid": "U-12",
                            "name": "Render",
                            "color": "#c084fc",
                            "classLabel": "Usuario",
                            "queueLabel": "Feedback 1",
                        },
                    ],
                },
                {
                    "id": "fila-f2",
                    "title": "Fila de feedback 2",
                    "kind": "Media prioridade",
                    "processes": [
                        {
                            "pid": "U-08",
                            "name": "Navegador",
                            "color": "#34d399",
                            "classLabel": "Usuario",
                            "queueLabel": "Feedback 2",
                        }
                    ],
                },
                {
                    "id": "fila-f3",
                    "title": "Fila de feedback 3",
                    "kind": "Baixa prioridade",
                    "processes": [
                        {
                            "pid": "U-01",
                            "name": "Backup",
                            "color": "#f472b6",
                            "classLabel": "Usuario",
                            "queueLabel": "Feedback 3",
                        }
                    ],
                },
                {
                    "id": "fila-bloqueados",
                    "title": "Bloqueados",
                    "kind": "Aguardando E/S",
                    "processes": [
                        {
                            "pid": "U-05",
                            "name": "Banco",
                            "color": "#fb7185",
                            "classLabel": "Usuario",
                            "queueLabel": "Disco 1",
                        },
                        {
                            "pid": "U-06",
                            "name": "Relatorios",
                            "color": "#a3e635",
                            "classLabel": "Usuario",
                            "queueLabel": "Disco 4",
                        },
                    ],
                },
                {
                    "id": "fila-finalizados",
                    "title": "Finalizados",
                    "kind": "Concluidos",
                    "processes": [
                        {
                            "pid": "U-02",
                            "name": "Logs",
                            "color": "#94a3b8",
                            "classLabel": "Usuario",
                            "queueLabel": "Finalizado",
                        }
                    ],
                },
            ],
            "memory": {
                "totalMb": 32768,
                "usedMb": 14336,
                "blocks": _build_memory_blocks(),
            },
            "disks": [
                {
                    "id": "disk-1",
                    "label": "Disco 1",
                    "activeProcess": {
                        "pid": "U-05",
                        "name": "Banco",
                        "color": "#fb7185",
                        "classLabel": "Usuario",
                        "queueLabel": "Disco 1",
                    },
                    "waitingQueue": [],
                },
                {
                    "id": "disk-2",
                    "label": "Disco 2",
                    "activeProcess": None,
                    "waitingQueue": [
                        {
                            "pid": "U-06",
                            "name": "Relatorios",
                            "color": "#a3e635",
                            "classLabel": "Usuario",
                            "queueLabel": "Disco 2",
                        }
                    ],
                },
                {
                    "id": "disk-3",
                    "label": "Disco 3",
                    "activeProcess": None,
                    "waitingQueue": [],
                },
                {
                    "id": "disk-4",
                    "label": "Disco 4",
                    "activeProcess": {
                        "pid": "U-04",
                        "name": "Exportacao",
                        "color": "#f97316",
                        "classLabel": "Usuario",
                        "queueLabel": "Disco 4",
                    },
                    "waitingQueue": [
                        {
                            "pid": "U-10",
                            "name": "Upload",
                            "color": "#38bdf8",
                            "classLabel": "Usuario",
                            "queueLabel": "Disco 4",
                        }
                    ],
                },
            ],
            "eventLog": [
                {"id": "e1", "time": 14, "message": "TR-01 criado e alocado na memoria principal."},
                {"id": "e2", "time": 15, "message": "U-07 entrou na CPU 2 a partir da fila de feedback 1."},
                {"id": "e3", "time": 16, "message": "U-05 bloqueado para operacao de disco no Disco 1."},
                {"id": "e4", "time": 17, "message": "U-03 consumiu o quantum e retornou para feedback 2."},
                {"id": "e5", "time": 18, "message": "CPU 4 ficou ociosa por ausencia de processo pronto."},
            ],
        }
    )


def _build_memory_blocks() -> list[dict[str, str | bool | None]]:
    occupied = [
        ("TR-01", "#ff6b57"),
        ("TR-02", "#f59e0b"),
        ("U-07", "#42d392"),
        ("U-07", "#42d392"),
        ("U-03", "#5cc8ff"),
        ("U-03", "#5cc8ff"),
        ("U-05", "#fb7185"),
        ("U-06", "#a3e635"),
        ("U-11", "#7dd3fc"),
        ("U-12", "#c084fc"),
        ("U-08", "#34d399"),
        ("U-01", "#f472b6"),
        ("U-01", "#f472b6"),
        ("U-12", "#c084fc"),
    ]

    blocks: list[dict[str, str | bool | None]] = []

    for index in range(32):
        label = f"{index + 1:02d}"

        if index < len(occupied):
            owner, color = occupied[index]
            blocks.append(
                {
                    "id": f"b{index + 1:02d}",
                    "label": label,
                    "occupied": True,
                    "ownerPid": owner,
                    "color": color,
                }
            )
            continue

        blocks.append(
            {
                "id": f"b{index + 1:02d}",
                "label": label,
                "occupied": False,
                "ownerPid": None,
                "color": None,
            }
        )

    return blocks
