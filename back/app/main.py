import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import ProcessDescriptor, SimulatorSnapshot
from .parser import DescriptorFormatError, parse_process_descriptors
from .simulator import SimulatorEngine

# Arquivo de entrada esperado pela professora.
# Localizado em examples/entrada.txt na raiz do projeto.
_ENTRADA_FILE = pathlib.Path(__file__).resolve().parent.parent.parent / "examples" / "entrada.txt"

# Rotas que o front usa para carregar, avancar e reiniciar a simulacao.
# As regras do trabalho ficam concentradas no SimulatorEngine.

app = FastAPI(
    title="Simulador de SO",
    version="1.0.0",
    description="Backend do simulador de escalonamento, memoria e discos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DescriptorInput(BaseModel):
    content: str


class DescriptorParseResponse(BaseModel):
    processes: list[ProcessDescriptor]
    warnings: list[str]


class LoadResponse(BaseModel):
    snapshot: SimulatorSnapshot
    warnings: list[str]


engine = SimulatorEngine()

if _ENTRADA_FILE.exists():
    try:
        engine.load(_ENTRADA_FILE.read_text(encoding="utf-8"))
    except DescriptorFormatError as _exc:
        engine.warnings = [f"examples/entrada.txt contém erro: {_exc}"]
else:
    engine.warnings = [
        f"Arquivo examples/entrada.txt não encontrado. "
        "Adicione o arquivo na pasta examples/ e reinicie o servidor."
    ]


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/snapshot", response_model=SimulatorSnapshot)
def get_snapshot() -> SimulatorSnapshot:
    return engine.snapshot()


@app.get("/api/default-input")
def get_default_input() -> dict[str, str]:
    return {"content": DEFAULT_INPUT}


@app.post("/api/load", response_model=LoadResponse)
def load_processes(payload: DescriptorInput) -> LoadResponse:
    try:
        snapshot = engine.load(payload.content)
    except DescriptorFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return LoadResponse(snapshot=snapshot, warnings=engine.warnings)


@app.post("/api/tick", response_model=SimulatorSnapshot)
def advance_tick() -> SimulatorSnapshot:
    return engine.tick()


@app.post("/api/step-back", response_model=SimulatorSnapshot)
def step_back() -> SimulatorSnapshot:
    return engine.step_back()


@app.post("/api/reset", response_model=SimulatorSnapshot)
def reset_simulation() -> SimulatorSnapshot:
    try:
        return engine.reset()
    except DescriptorFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/processes/parse", response_model=DescriptorParseResponse)
def parse_descriptors(payload: DescriptorInput) -> DescriptorParseResponse:
    try:
        parsed = parse_process_descriptors(payload.content)
    except DescriptorFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DescriptorParseResponse(
        processes=parsed.processes,
        warnings=parsed.warnings,
    )
