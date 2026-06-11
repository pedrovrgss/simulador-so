from dataclasses import dataclass

from .models import DiskSnapshot, ProcessCard

# Controle simples dos 4 discos.
# Enquanto o processo estiver usando I/O, o disco fica reservado para ele.

TOTAL_DISKS = 4


@dataclass
class Disk:
    id: int
    owner_pid: str | None = None


class DiskManager:
    def __init__(self, total_disks: int = TOTAL_DISKS) -> None:
        # Cada disco guarda apenas qual processo esta usando ele no momento.
        self.disks = []
        for index in range(total_disks):
            self.disks.append(Disk(id=index + 1))

    def reserve(self, pid: str, amount: int) -> bool:
        # Processo sem I/O nao precisa reservar disco.
        if amount == 0:
            return True

        # Sem disco livre suficiente, o processo fica na fila de recurso.
        if len(self.available_disks()) < amount:
            return False

        for disk in self.available_disks()[:amount]:
            disk.owner_pid = pid

        return True

    def release(self, pid: str) -> None:
        # Quando o processo finaliza, todos os discos dele voltam a ficar livres.
        for disk in self.disks:
            if disk.owner_pid == pid:
                disk.owner_pid = None

    def owners_disks(self, pid: str) -> list[int]:
        disk_ids: list[int] = []
        for disk in self.disks:
            if disk.owner_pid == pid:
                disk_ids.append(disk.id)
        return disk_ids

    def available_disks(self) -> list[Disk]:
        available: list[Disk] = []
        for disk in self.disks:
            if disk.owner_pid is None:
                available.append(disk)
        return available

    def to_snapshot(
        self,
        *,
        process_cards: dict[str, ProcessCard],
        active_io_pids: list[str],
        waiting_resource_pids: list[str],
    ) -> list[DiskSnapshot]:
        snapshots: list[DiskSnapshot] = []

        for disk in self.disks:
            status = "livre"
            owner_process = None
            active_process = None

            if disk.owner_pid is not None:
                owner_process = process_cards.get(disk.owner_pid)
                status = "reservado"

                # Se o dono tambem esta bloqueado em I/O, o disco esta em uso agora.
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
                    waitingQueue=_waiting_cards_for_disk(
                        disk,
                        waiting_resource_pids,
                        process_cards,
                    ),
                )
            )

        return snapshots


def _waiting_cards_for_disk(
    disk: Disk,
    waiting_resource_pids: list[str],
    process_cards: dict[str, ProcessCard],
) -> list[ProcessCard]:
    waiting_cards: list[ProcessCard] = []

    if disk.owner_pid is not None:
        return waiting_cards

    for pid in waiting_resource_pids:
        if pid in process_cards:
            waiting_cards.append(process_cards[pid])

    return waiting_cards
