from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import ProcessDescriptor, SimulatorSnapshot
from .parser import DescriptorFormatError, parse_process_descriptors
from .sample_data import build_sample_snapshot

app = FastAPI(
    title="Simulador de SO",
    version="0.1.0",
    description="Backend inicial para simulacao de escalonamento, memoria e discos.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DescriptorInput(BaseModel):
    content: str


class DescriptorParseResponse(BaseModel):
    processes: list[ProcessDescriptor]
    warnings: list[str]


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/snapshot", response_model=SimulatorSnapshot)
def get_snapshot() -> SimulatorSnapshot:
    return build_sample_snapshot()


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
