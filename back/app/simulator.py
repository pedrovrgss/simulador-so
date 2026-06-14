import copy

from . import admission, execution
from .memory import MemoryManager
from .models import EventEntry, SimulatorSnapshot
from .parser import parse_process_descriptors
from .resources import DiskManager
from .runtime import CpuRuntime, ProcessRuntime, ProcessState
from .sample_data import DEFAULT_INPUT
from .scheduler import Scheduler
from .snapshot import build_snapshot

# Limite de entradas no historico para nao crescer indefinidamente.
MAX_HISTORY = 200


class SimulatorEngine:
    """
    Junta as partes do simulador.
    A ideia foi deixar cada regra grande em um arquivo separado.
    """

    def __init__(self) -> None:
        self.current_input = DEFAULT_INPUT
        self.warnings: list[str] = []
        self._history: list[dict] = []
        self.reset()

    # Ciclo principal

    def load(self, content: str) -> SimulatorSnapshot:
        old_input = self.current_input
        self.current_input = content

        try:
            return self.reset()
        except Exception:
            self.current_input = old_input
            self.reset()
            raise

    def reset(self) -> SimulatorSnapshot:
        self._history = []
        self.clock = 0
        self.memory = MemoryManager()
        self.disks = DiskManager()
        self.scheduler = Scheduler()
        self.cpus = []
        for index in range(4):
            self.cpus.append(CpuRuntime(id=index + 1))

        self.processes: dict[str, ProcessRuntime] = {}
        self.pending_processes: list = []
        self.waiting_memory: list[str] = []
        self.loading_memory: list[str] = []
        self.blocked_io: list[str] = []
        # Processos que saíram da CPU para I/O mas cujo(s) drive(s) estão ocupados.
        self.blocked_disk: list[str] = []
        self.finished: list[str] = []
        self.rejected: list[str] = []
        self.events: list[EventEntry] = []
        self._event_id = 0

        parsed = parse_process_descriptors(self.current_input)
        self.warnings = parsed.warnings

        admission.preparar_processos(self, parsed)
        admission.admitir_chegadas(self)
        admission.tentar_processos_em_espera(self)
        execution.despachar_cpus_livres(self)

        return self.snapshot()

    def tick(self) -> SimulatorSnapshot:
        if self.is_finished():
            return self.snapshot()

        # Salva o estado atual antes de avançar.
        if len(self._history) >= MAX_HISTORY:
            self._history.pop(0)
        self._history.append(self._save_state())

        self.clock += 1
        # Processos que terminaram a transferencia DMA no tick anterior entram na fila pronto.
        admission.avancar_carregamento_memoria(self)
        admission.admitir_chegadas(self)
        execution.avancar_io(self)
        execution.avancar_cpus(self)
        admission.tentar_processos_em_espera(self)
        execution.despachar_cpus_livres(self)

        return self.snapshot()

    def step_back(self) -> SimulatorSnapshot:
        """Restaura o estado do tick anterior."""
        if not self._history:
            return self.snapshot()

        self._restore_state(self._history.pop())
        return self.snapshot()

    def has_history(self) -> bool:
        return len(self._history) > 0

    def is_finished(self) -> bool:
        if self.pending_processes:
            return False
        for cpu in self.cpus:
            if cpu.pid:
                return False
        if self.scheduler.has_ready_process() or self.blocked_io or self.blocked_disk:
            return False
        if self.waiting_memory or self.loading_memory:
            return False
        return len(self.finished) + len(self.rejected) == len(self.processes)

    # Saida para tela

    def snapshot(self) -> SimulatorSnapshot:
        return build_snapshot(
            clock=self.clock,
            cpus=self.cpus,
            processes=self.processes,
            scheduler=self.scheduler,
            memory=self.memory,
            disks=self.disks,
            blocked_io=self.blocked_io,
            blocked_disk=self.blocked_disk,
            waiting_memory=self.waiting_memory,
            loading_memory=self.loading_memory,
            finished=self.finished,
            rejected=self.rejected,
            events=self.events,
            warnings=self.warnings,
        )

    def change_state(self, process: ProcessRuntime, new_state: ProcessState) -> None:
        # Cada transicao ja tem um log explicito no codigo que a origina.
        # Aqui apenas atualizamos o campo; nao geramos mensagem automatica.
        process.state = new_state

    def log_event(self, message: str) -> None:
        self._event_id += 1
        self.events.append(
            EventEntry(
                id=f"e{self._event_id}",
                time=self.clock,
                message=message,
            )
        )

    # Historico interno

    def _save_state(self) -> dict:
        return {
            "clock": self.clock,
            "memory": copy.deepcopy(self.memory),
            "disks": copy.deepcopy(self.disks),
            "scheduler": copy.deepcopy(self.scheduler),
            "cpus": copy.deepcopy(self.cpus),
            "processes": copy.deepcopy(self.processes),
            "pending_processes": copy.deepcopy(self.pending_processes),
            "waiting_memory": list(self.waiting_memory),
            "loading_memory": list(self.loading_memory),
            "blocked_io": list(self.blocked_io),
            "blocked_disk": list(self.blocked_disk),
            "finished": list(self.finished),
            "rejected": list(self.rejected),
            "events": list(self.events),
            "_event_id": self._event_id,
        }

    def _restore_state(self, state: dict) -> None:
        self.clock = state["clock"]
        self.memory = state["memory"]
        self.disks = state["disks"]
        self.scheduler = state["scheduler"]
        self.cpus = state["cpus"]
        self.processes = state["processes"]
        self.pending_processes = state["pending_processes"]
        self.waiting_memory = state["waiting_memory"]
        self.loading_memory = state["loading_memory"]
        self.blocked_io = state["blocked_io"]
        self.blocked_disk = state["blocked_disk"]
        self.finished = state["finished"]
        self.rejected = state["rejected"]
        self.events = state["events"]
        self._event_id = state["_event_id"]
