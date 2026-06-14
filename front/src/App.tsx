import { useEffect, useState } from 'react'
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

  useEffect(() => {
    let active = true

    fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/snapshot`)
      .then((s) => { if (active) setSnapshot(s) })
      .catch(() => { /* backend indisponivel; usa fallback */ })

    return () => { active = false }
  }, [])

  useEffect(() => {
    if (isPaused) return

    const interval = window.setInterval(() => {
      void fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/tick`, { method: 'POST' })
        .then((next) => setSnapshot(next))
        .catch(() => setIsPaused(true))
    }, 1000 / speed)

    return () => { window.clearInterval(interval) }
  }, [isPaused, speed])

  async function advanceTick() {
    const next = await fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/tick`, { method: 'POST' })
    setSnapshot(next)
  }

  function handleTogglePause() {
    setIsPaused((v) => !v)
  }

  function handleIncreaseSpeed() {
    setSpeed((current) => {
      const next = (SPEED_STEPS.indexOf(current) + 1) % SPEED_STEPS.length
      return SPEED_STEPS[next]
    })
  }

  async function handleReset() {
    const s = await fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/reset`, { method: 'POST' })
    setSnapshot(s)
    setSpeed(INITIAL_SPEED)
    setIsPaused(true)
  }

  async function handleStepBackward() {
    if (!isPaused) return
    const s = await fetchJson<SimulatorSnapshot>(`${API_BASE_URL}/step-back`, { method: 'POST' })
    setSnapshot(s)
  }

  function handleStepForward() {
    if (!isPaused) return
    void advanceTick()
  }

  return (
    <main aria-label="Tela inicial do simulador" className="min-h-screen px-4 py-5">
      <div className="mx-auto flex w-full max-w-[94rem] flex-col items-center gap-5">
        <SimulationHeader
          elapsedTime={snapshot.clock}
          isPaused={isPaused}
          speed={speed}
          canStepBackward={snapshot.clock > 0}
          onReset={handleReset}
          onStepBackward={handleStepBackward}
          onStepForward={handleStepForward}
          onTogglePause={handleTogglePause}
          onIncreaseSpeed={handleIncreaseSpeed}
        />

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
