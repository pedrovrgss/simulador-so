from dataclasses import dataclass

from .models import DiskSnapshot, ProcessCard

# 4 discos fisicos conforme os requisitos do simulador.
# O disco tem tamanho ilimitado: a reserva nunca falha por falta de espaco.
# Um processo nunca fica no estado ESPERANDO_RECURSO.

TOTAL_DISKS = 4


@dataclass
class Disk:
    id: int
    owner_pid: str | None = None


class DiskManager:
    def __init__(self, total_disks: int = TOTAL_DISKS) -> None:
        self.disks = [Disk(id=i + 1) for i in range(total_disks)]

    def reserve(self, pid: str, amount: int) -> bool:
        # Disco de tamanho ilimitado: a reserva SEMPRE e bem-sucedida.
        # Atribuimos aos discos livres disponiveis; se nao houver livres
        # suficientes, ainda retornamos True (o disco absorve qualquer carga).
        if amount == 0:
            return True

        free = self.available_disks()
        for disk in free[:amount]:
            disk.owner_pid = pid

        return True  # nunca bloqueia o processo

    def release(self, pid: str) -> None:
        # Quando o processo finaliza, os discos alocados voltam a ficar livres.
        for disk in self.disks:
            if disk.owner_pid == pid:
                disk.owner_pid = None

    def owners_disks(self, pid: str) -> list[int]:
        return [disk.id for disk in self.disks if disk.owner_pid == pid]

    def available_disks(self) -> list[Disk]:
        return [disk for disk in self.disks if disk.owner_pid is None]

    def to_snapshot(
        self,
        *,
        process_cards: dict[str, ProcessCard],
        active_io_pids: list[str],
    ) -> list[DiskSnapshot]:
        snapshots: list[DiskSnapshot] = []

        for disk in self.disks:
            status = "livre"
            owner_process = None
            active_process = None

            if disk.owner_pid is not None:
                owner_process = process_cards.get(disk.owner_pid)
                status = "reservado"

                # Se o dono esta em I/O agora, o disco aparece em uso.
                if disk.owner_pid in active_io_pids:
                    status = "io"
                    active_process = owner_process

            snapshots.append(
                DiskSnapshot(
                    id=f"disk-{disk.id}",
                    label=f"Disco {disk.id}",
                    status=status,
                    ownerProcess=owner_process,
                    activeProcess=active_process,
                    waitingQueue=[],  # nunca ha fila de espera por disco
                )
            )

        return snapshots
