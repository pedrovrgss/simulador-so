from dataclasses import dataclass

from .models import ProcessDescriptor

# Dados que mudam durante a simulacao.
# Este arquivo nao decide escalonamento; ele so guarda o estado atual.

ProcessState = str


@dataclass
class CpuRuntime:
    id: int
    pid: str | None = None
    quantum_left: int | None = None

    def clear(self) -> None:
        # CPU livre nao tem processo nem quantum contando.
        self.pid = None
        self.quantum_left = None


@dataclass
class ProcessRuntime:
    # descriptor tem os dados fixos da entrada; os outros campos mudam no tick.
    descriptor: ProcessDescriptor
    pid: str
    display_pid: str
    color: str
    priority: int
    memory_mb: int
    disks_required: int
    is_real_time: bool
    state: ProcessState = "NOVO"
    queue_level: int = 0
    phase: str = "fase_cpu_1"
    cpu1_remaining: int = 0
    io_remaining: int = 0
    cpu2_remaining: int = 0

    def current_cpu_remaining(self) -> int:
        # A tela e a execucao precisam saber qual fase de CPU esta ativa agora.
        if self.phase == "fase_cpu_2":
            return self.cpu2_remaining
        return self.cpu1_remaining

    def decrease_cpu(self) -> None:
        # Cada tick de CPU gasta uma unidade da fase atual.
        if self.phase == "fase_cpu_2":
            self.cpu2_remaining -= 1
        else:
            self.cpu1_remaining -= 1

    def total_for_current_phase(self) -> int:
        # Usado para calcular a barra de progresso da CPU no frontend.
        if self.phase == "fase_cpu_2":
            return self.descriptor.cpu_burst_2
        return self.descriptor.cpu_burst_1
