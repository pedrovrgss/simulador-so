# Entrada padrao para mostrar as partes principais na apresentacao:
# tempo real, usuario, I/O, memoria e disputa por disco.

DEFAULT_INPUT = """# [id, prioridade, cpu1, io, cpu2, ram, discos]
[1, 0, 5, 0, 0, 512, 0]
[2, 1, 6, 3, 4, 1024, 1]
[3, 1, 10, 0, 0, 2048, 0]
[4, 1, 3, 4, 3, 4096, 1]
[5, 0, 4, 0, 0, 256, 0]
[6, 1, 8, 2, 2, 8192, 2]
[7, 1, 15, 0, 0, 1200, 0]
[8, 1, 2, 6, 2, 16384, 1]
[9, 1, 5, 3, 5, 2048, 1]
[10, 1, 12, 0, 0, 4096, 0]
[11, 1, 4, 2, 4, 1024, 1]
[12, 1, 7, 0, 0, 2048, 0]
"""

PROCESS_COLORS = [
    "#ff6b57",
    "#42d392",
    "#5cc8ff",
    "#a78bfa",
    "#f59e0b",
    "#34d399",
    "#f472b6",
    "#c084fc",
    "#fb7185",
    "#38bdf8",
    "#a3e635",
    "#94a3b8",
]
