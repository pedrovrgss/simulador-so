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

    def used_mib(self) -> int:
        total = 0
        for segment in self.segments:
            if not segment.is_free():
                total += segment.size
        return total

    def to_snapshot(self) -> MemorySnapshot:
        return MemorySnapshot(
            totalMb=self.total_mib,
            usedMb=self.used_mib(),
            blocks=self._build_view_blocks(),
        )

    def _merge_free_segments(self) -> None:
        merged: list[MemorySegment] = []

        for segment in self.segments:
            if merged and merged[-1].is_free() and segment.is_free():
                merged[-1].size += segment.size
            else:
                merged.append(segment)

        self.segments = merged

    def _build_view_blocks(self) -> list[MemoryBlock]:
        # A simulacao usa tamanhos reais em MiB, mas a tela mostra 32 faixas.
        block_size = self.total_mib // MEMORY_VIEW_BLOCKS
        blocks: list[MemoryBlock] = []

        for index in range(MEMORY_VIEW_BLOCKS):
            start = index * block_size
            end = start + block_size
            owner = self._owner_for_range(start, end)

            blocks.append(
                MemoryBlock(
                    id=f"b{index + 1:02d}",
                    label=f"{index + 1:02d}",
                    occupied=owner is not None,
                    ownerPid=owner.pid if owner else None,
                    color=owner.color if owner else None,
                )
            )

        return blocks

    def _owner_for_range(self, start: int, end: int) -> MemorySegment | None:
        for segment in self.segments:
            if segment.is_free():
                continue
            # Se o segmento ocupado cruza a faixa visual, ela aparece ocupada.
            if segment.start < end and segment.end() > start:
                return segment

        return None
