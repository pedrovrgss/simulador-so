from dataclasses import dataclass

# Controle dos 4 drives de disco para operacoes de I/O.
# Um disco so e marcado como ocupado durante a fase de I/O efetiva do processo,
# nao desde a chegada. A exibicao no painel usa home_disk_id de cada ProcessRuntime.

TOTAL_DISKS = 4


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
