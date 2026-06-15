from dataclasses import dataclass

# Controle dos drives de disco e dos canais DMA do sistema.
# Os 2 canais DMA sao compartilhados entre carregamento de memoria e I/O em disco.

TOTAL_DISKS = 4
TOTAL_DMA_CHANNELS = 2


@dataclass
class Disk:
    id: int
    io_pid: str | None = None   # processo atualmente fazendo I/O neste drive


class DiskManager:
    def __init__(self, total_disks: int = TOTAL_DISKS) -> None:
        self.disks = [Disk(id=i + 1) for i in range(total_disks)]

    def can_acquire(self, disk_ids: list[int]) -> bool:
        """Verifica se todos os drives solicitados estao livres."""
        if not disk_ids:
            return True
        return all(self._get(d).io_pid is None for d in disk_ids)

    def acquire_io(self, pid: str, disk_ids: list[int]) -> None:
        """Marca os drives como em uso pelo processo durante o I/O."""
        for d in disk_ids:
            self._get(d).io_pid = pid

    def release_io(self, pid: str) -> None:
        """Libera todos os drives que o processo estava usando."""
        for disk in self.disks:
            if disk.io_pid == pid:
                disk.io_pid = None

    def active_io_pid(self, disk_id: int) -> str | None:
        """Retorna o pid do processo fazendo I/O neste drive, ou None."""
        return self._get(disk_id).io_pid

    def _get(self, disk_id: int) -> Disk:
        return self.disks[disk_id - 1]


@dataclass
class DMAChannel:
    id: int
    pid: str | None = None


class DMAManager:
    def __init__(self, total: int = TOTAL_DMA_CHANNELS) -> None:
        self.channels = [DMAChannel(id=i + 1) for i in range(total)]

    def available(self) -> bool:
        return any(ch.pid is None for ch in self.channels)

    def acquire(self, pid: str) -> None:
        for ch in self.channels:
            if ch.pid is None:
                ch.pid = pid
                return

    def release(self, pid: str) -> None:
        for ch in self.channels:
            if ch.pid == pid:
                ch.pid = None
                return

    def in_use(self) -> int:
        return sum(1 for ch in self.channels if ch.pid is not None)
