from . import admission, execution
from .memory import MemoryManager
from .models import EventEntry, SimulatorSnapshot
from .parser import parse_process_descriptors
from .resources import DiskManager
from .runtime import CpuRuntime, ProcessRuntime, ProcessState
from .sample_data import DEFAULT_INPUT
from .scheduler import Scheduler
from .snapshot import build_snapshot

STATE_LABELS = {
    "NOVO": "novo",
    "PRONTO": "pronto",
    "EXECUTANDO": "executando",
    "BLOQUEADO_IO": "bloqueado em I/O",
    "ESPERANDO_MEMORIA": "esperando memoria",
    "FINALIZADO": "finalizado",
    "REJEITADO": "rejeitado",
}


class SimulatorEngine:
    """
    Junta as partes do simulador.
    A ideia foi deixar cada regra grande em um arquivo separado.
    """

    def __init__(self) -> None:
        self.current_input = DEFAULT_INPUT
        self.warnings: list[str] = []
        self.reset()

    # Ciclo principal

    def load(self, content: str) -> SimulatorSnapshot:
        old_input = self.current_input
        self.current_input = content

        try:
            return self.reset()
        except Exception:
            # Se a nova entrada for invalida, mantemos a simulacao anterior.
            self.current_input = old_input
            self.reset()
            raise

    def reset(self) -> SimulatorSnapshot:
        # Reset recria todos os controladores para voltar ao tick 0.
        self.clock = 0
        self.memory = MemoryManager()
        self.disks = DiskManager()
        self.scheduler = Scheduler()
        self.cpus = []
        for index in range(4):
            self.cpus.append(CpuRuntime(id=index + 1))

        self.processes: dict[str, ProcessRuntime] = {}
        self.waiting_memory: list[str] = []
        self.blocked_io: list[str] = []
        self.finished: list[str] = []
        self.rejected: list[str] = []
        self.events: list[EventEntry] = []
        self._event_id = 0

        parsed = parse_process_descriptors(self.current_input)
        self.warnings = parsed.warnings

        # Todos os processos chegam no tempo 0, entao criamos todos no reset.
        admission.criar_processos(self, parsed)
        admission.tentar_processos_em_espera(self)
        execution.despachar_cpus_livres(self)

        return self.snapshot()

    def tick(self) -> SimulatorSnapshot:
        if self.is_finished():
            return self.snapshot()

        # Cada tick vale uma unidade de tempo da simulacao.
        self.clock += 1
        # A ordem aqui importa: primeiro termina o que estava rodando,
        # depois tentamos liberar espera e ocupar CPUs livres.
        execution.avancar_io(self)
        execution.avancar_cpus(self)
        admission.tentar_processos_em_espera(self)
        execution.despachar_cpus_livres(self)

        return self.snapshot()

    def is_finished(self) -> bool:
        # A simulacao so acaba quando nao existe processo rodando ou esperando.
        for cpu in self.cpus:
            if cpu.pid:
                return False
        if self.scheduler.has_ready_process() or self.blocked_io:
            return False
        if self.waiting_memory:
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
            waiting_memory=self.waiting_memory,
            finished=self.finished,
            rejected=self.rejected,
            events=self.events,
        )

    def change_state(self, process: ProcessRuntime, new_state: ProcessState) -> None:
        # Evita poluir o log repetindo o mesmo estado varias vezes.
        if process.state == new_state:
            return

        old_state = process.state
        process.state = new_state
        old_label = STATE_LABELS.get(old_state, old_state.lower())
        new_label = STATE_LABELS.get(new_state, new_state.lower())
        self.log_event(
            f"{process.display_pid}: mudou de {old_label} para {new_label}."
        )

    def log_event(self, message: str) -> None:
        self._event_id += 1
        self.events.append(
            EventEntry(
                id=f"e{self._event_id}",
                time=self.clock,
                message=message,
            )
        )
