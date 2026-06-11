import { useEffect, useState, type ChangeEvent } from 'react'
import { CpuCard } from './components/CpuCard'
import { MainMemoryPanel } from './components/MainMemoryPanel'
import { SimulationHeader } from './components/SimulationHeader'
import { fallbackSnapshot } from './data/fallbackSnapshot'
import { SchedulingQueues } from './components/SchedulingQueues'
import { EventLog } from './components/EventLog'
import { DisksPanel } from './components/DisksPanel'
import type { SimulatorSnapshot } from './types/simulator'

const SPEED_STEPS = [1, 2, 4, 8]
const INITIAL_SPEED = 1
const API_BASE_URL = 'http://localhost:8000/api'

const LOCAL_DEFAULT_INPUT = `# [id, prioridade, cpu1, io, cpu2, ram, discos]
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
[12, 1, 7, 0, 0, 2048, 0]`

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `Falha HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

function App() {
  const [snapshot, setSnapshot] = useState<SimulatorSnapshot>(fallbackSnapshot)
  const [isPaused, setIsPaused] = useState(true)
  const [speed, setSpeed] = useState(INITIAL_SPEED)
  const [inputText, setInputText] = useState(LOCAL_DEFAULT_INPUT)
  const [error, setError] = useState<string | null>(null)
  const [warnings, setWarnings] = useState<string[]>([])

  useEffect(() => {
    let active = true

    async function loadInitialState() {
      try {
        const [initialSnapshot, defaultInput] = await Promise.all([
          fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/snapshot`),
          fetchJson<{ content: string }>(`${API_BASE_URL}/default-input`),
        ])

        if (!active) return
        setSnapshot(initialSnapshot)
        setInputText(defaultInput.content.trim())
        setError(null)
      } catch (loadError) {
        if (!active) return
        setError(loadError instanceof Error ? loadError.message : 'Falha ao carregar API')
      }
    }

    void loadInitialState()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (isPaused) return

    const interval = window.setInterval(() => {
      void fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/tick`, { method: 'POST' })
        .then((nextSnapshot) => {
          setSnapshot(nextSnapshot)
          setError(null)
        })
        .catch((tickError) => {
          setIsPaused(true)
          setError(tickError instanceof Error ? tickError.message : 'Falha ao avancar')
        })
    }, 1000 / speed)

    return () => {
      window.clearInterval(interval)
    }
  }, [isPaused, speed])

  async function advanceTick() {
    try {
      const nextSnapshot = await fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/tick`, {
        method: 'POST',
      })
      setSnapshot(nextSnapshot)
      setError(null)
    } catch (tickError) {
      setIsPaused(true)
      setError(tickError instanceof Error ? tickError.message : 'Falha ao avancar')
    }
  }

  function handleTogglePause() {
    setIsPaused((currentValue) => !currentValue)
  }

  function handleIncreaseSpeed() {
    setSpeed((currentSpeed) => {
      const currentIndex = SPEED_STEPS.indexOf(currentSpeed)
      const nextIndex = (currentIndex + 1) % SPEED_STEPS.length
      return SPEED_STEPS[nextIndex]
    })
  }

  async function handleReset() {
    try {
      const resetSnapshot = await fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/reset`, {
        method: 'POST',
      })
      setSnapshot(resetSnapshot)
      setSpeed(INITIAL_SPEED)
      setIsPaused(true)
      setError(null)
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : 'Falha ao reiniciar')
    }
  }

  function handleStepBackward() {
    return
  }

  function handleStepForward() {
    if (!isPaused) return
    void advanceTick()
  }

  async function handleLoadInput() {
    try {
      const result = await fetchJson<{ snapshot: SimulatorSnapshot, warnings: string[] }>(
        `${API_BASE_URL}/load`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: inputText }),
        },
      )
      setSnapshot(result.snapshot)
      setWarnings(result.warnings)
      setSpeed(INITIAL_SPEED)
      setIsPaused(true)
      setError(null)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Falha ao carregar entrada')
    }
  }

  async function handleFileInputChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const content = await file.text()
      setInputText(content.trim())
      setWarnings([])
      setError(null)
    } catch {
      setError('Falha ao ler arquivo .txt')
    } finally {
      event.target.value = ''
    }
  }

  return (
    <main aria-label="Tela inicial do simulador" className="min-h-screen px-4 py-5">
      <div className="mx-auto flex w-full max-w-[94rem] flex-col items-center gap-5">
        <SimulationHeader
          elapsedTime={snapshot.clock}
          isPaused={isPaused}
          speed={speed}
          canStepBackward={false}
          onReset={handleReset}
          onStepBackward={handleStepBackward}
          onStepForward={handleStepForward}
          onTogglePause={handleTogglePause}
          onIncreaseSpeed={handleIncreaseSpeed}
        />

        <section className="grid w-full grid-cols-1 gap-3 xl:grid-cols-[minmax(24rem,1fr)_17rem]">
          <div className="flex flex-col gap-2 rounded-md border border-white/10 bg-white/4 p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">
                Entrada de processos
              </p>
              <div className="flex flex-wrap justify-end gap-2">
                <label className="cursor-pointer rounded-md border border-white/10 bg-white/6 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:bg-white/10">
                  Abrir .txt
                  <input
                    type="file"
                    accept=".txt,text/plain"
                    className="sr-only"
                    onChange={handleFileInputChange}
                  />
                </label>
                <button
                  type="button"
                  onClick={handleLoadInput}
                  className="rounded-md border border-sky-400/20 bg-sky-400/10 px-3 py-1.5 text-xs font-semibold text-sky-100 transition hover:bg-sky-400/16"
                >
                  Carregar entrada
                </button>
              </div>
            </div>
            <textarea
              value={inputText}
              onChange={(event) => setInputText(event.target.value)}
              spellCheck={false}
              className="h-24 resize-none rounded-sm border border-white/10 bg-black/40 p-2 font-mono text-[0.68rem] leading-relaxed text-slate-300 outline-none transition focus:border-sky-400/40"
            />
          </div>

          <div className="flex w-[17rem] flex-col justify-center gap-1 rounded-md border border-white/10 bg-white/4 px-3 py-2">
            <p className="text-[0.6rem] uppercase tracking-[0.22em] text-slate-500">status</p>
            <p className="text-[0.68rem] text-slate-400">
              {error ?? (warnings[0] ?? 'Backend conectado')}
            </p>
          </div>
        </section>

        <section className="grid w-full grid-cols-1 gap-4 2xl:grid-cols-[minmax(35rem,42rem)_minmax(32rem,1fr)_17rem]">
          <div className="flex min-w-0 flex-col gap-6">
            <div className="flex flex-wrap gap-2">
              {snapshot.cpus.map((cpu) => (
                <CpuCard key={cpu.id} cpu={cpu} />
              ))}
            </div>

            <div className="flex-1">
              <SchedulingQueues queues={snapshot.queues} />
            </div>
          </div>

          <div className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-[minmax(22rem,1fr)_minmax(22rem,1fr)] 2xl:flex 2xl:flex-col">
            <div className="h-[10.5rem] xl:h-full 2xl:h-[10.5rem]">
              <EventLog events={snapshot.eventLog} />
            </div>
            <div className="min-h-[18rem] min-w-[22rem] 2xl:flex-1">
              <DisksPanel disks={snapshot.disks} />
            </div>
          </div>

          <div className="w-full 2xl:w-auto">
            <MainMemoryPanel memory={snapshot.memory} />
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
