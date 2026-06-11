# Filas de pronto.
# TR fica em FCFS; usuario fica no feedback com tres niveis.

QUANTUM_USUARIO = 2


def nome_fila(queue_name: str) -> str:
    # Nome mais claro para aparecer no log da simulacao.
    if queue_name == "FCFS":
        return "fila tempo real (FCFS)"

    if queue_name.startswith("U") and queue_name[1:].isdigit():
        level = int(queue_name[1:]) + 1
        return f"fila {level} do feedback"

    return queue_name


class Scheduler:
    def __init__(self) -> None:
        # Tempo real fica separado porque tem prioridade sobre usuario.
        self.real_time: list[str] = []
        # user_queues[0] e a fila mais alta; user_queues[2] e a mais baixa.
        self.user_queues: list[list[str]] = [[], [], []]

    def add_ready(self, pid: str, priority: int, queue_level: int = 0) -> str:
        # Prioridade 0 representa tempo real no trabalho.
        if priority == 0:
            self.real_time.append(pid)
            return "FCFS"

        # Garante que usuario sempre fique entre as tres filas do feedback.
        level = max(0, min(2, queue_level))
        self.user_queues[level].append(pid)
        return f"U{level}"

    def next_process(self) -> tuple[str, str] | None:
        # Processo de tempo real tem prioridade sobre usuario.
        if self.real_time:
            return self.real_time.pop(0), "FCFS"

        # Se nao tiver TR, procura da fila de usuario mais alta para a mais baixa.
        for index, queue in enumerate(self.user_queues):
            if queue:
                return queue.pop(0), f"U{index}"

        return None

    def has_ready_process(self) -> bool:
        if self.real_time:
            return True

        for queue in self.user_queues:
            if queue:
                return True

        return False

    def queue_items(self) -> dict[str, list[str]]:
        return {
            "FCFS": list(self.real_time),
            "U0": list(self.user_queues[0]),
            "U1": list(self.user_queues[1]),
            "U2": list(self.user_queues[2]),
        }
