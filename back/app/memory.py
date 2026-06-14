from dataclasses import dataclass

from .models import MemoryBlock, MemorySnapshot

# Memoria principal do simulador.
# Guardamos blocos contiguos para ficar facil explicar o First Fit.

MEMORIA_TOTAL_MIB = 32768
MEMORY_VIEW_BLOCKS = 32


@dataclass
class MemorySegment:
    start: int
    size: int
    pid: str | None = None
    color: str | None = None

    def is_free(self) -> bool:
        return self.pid is None

    def end(self) -> int:
        return self.start + self.size


class MemoryManager:
    def __init__(self, total_mib: int = MEMORIA_TOTAL_MIB) -> None:
        self.total_mib = total_mib
        # No inicio toda a memoria e um unico bloco livre.
        self.segments = [MemorySegment(start=0, size=total_mib)]

    def allocate(self, pid: str, size: int, color: str) -> bool:
        # First Fit: usa o primeiro espaco livre onde o processo couber.
        for index, segment in enumerate(self.segments):
            if not segment.is_free() or segment.size < size:
                continue

            allocated = MemorySegment(
                start=segment.start,
                size=size,
                pid=pid,
                color=color,
            )

            remaining_size = segment.size - size
            if remaining_size > 0:
                # Se sobrou espaco no bloco, dividimos em ocupado + livre.
                remaining = MemorySegment(
                    start=segment.start + size,
                    size=remaining_size,
                )
                self.segments[index:index + 1] = [allocated, remaining]
            else:
                self.segments[index] = allocated

            return True

        return False

    def free(self, pid: str) -> None:
        # Ao finalizar, o processo deixa de ser dono dos seus blocos.
        for segment in self.segments:
            if segment.pid == pid:
                segment.pid = None
                segment.color = None

        # Juntar blocos livres evita falsa falta de memoria por fragmentacao.
        self._merge_free_segments()

    def has_allocation(self, pid: str) -> bool:
        for segment in self.segments:
            if segment.pid == pid:
                return True
        return False

    def used_mib(self, hidden_pids: frozenset[str] = frozenset()) -> int:
        total = 0
        for segment in self.segments:
            if not segment.is_free() and segment.pid not in hidden_pids:
                total += segment.size
        return total

    def to_snapshot(self, hidden_pids: frozenset[str] = frozenset()) -> MemorySnapshot:
        """hidden_pids: display_pids de processos em DMA — reservados mas ainda nao visiveis."""
        return MemorySnapshot(
            totalMb=self.total_mib,
            usedMb=self.used_mib(hidden_pids=hidden_pids),
            blocks=self._build_view_blocks(hidden_pids=hidden_pids),
        )

    def _merge_free_segments(self) -> None:
        merged: list[MemorySegment] = []

        for segment in self.segments:
            if merged and merged[-1].is_free() and segment.is_free():
                merged[-1].size += segment.size
            else:
                merged.append(segment)

        self.segments = merged

    def _build_view_blocks(self, hidden_pids: frozenset[str] = frozenset()) -> list[MemoryBlock]:
        # Segmentos em hidden_pids sao tratados como livres visualmente (DMA em curso).
        # Segmentos livres adjacentes sao mesclados para nao fragmentar o display.
        visual: list[dict] = []
        for seg in self.segments:
            show_free = seg.is_free() or seg.pid in hidden_pids
            if visual and visual[-1]["free"] and show_free:
                visual[-1]["size"] += seg.size  # mescla com o livre anterior
            else:
                visual.append({
                    "start": seg.start,
                    "size": seg.size,
                    "free": show_free,
                    "pid": None if show_free else seg.pid,
                    "color": None if show_free else seg.color,
                })

        return [
            MemoryBlock(
                id=f"seg-{i}",
                startMb=v["start"],
                sizeMb=v["size"],
                occupied=not v["free"],
                ownerPid=v["pid"],
                color=v["color"],
            )
            for i, v in enumerate(visual)
        ]
