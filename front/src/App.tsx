import { useEffect, useState } from 'react'
import { CpuCard } from './components/CpuCard'
import { MainMemoryPanel } from './components/MainMemoryPanel'
import { SimulationHeader } from './components/SimulationHeader'
import type { MainMemoryInfo } from './types/memory'
import type { ProcessorInfo } from './types/processor'

const SPEED_STEPS = [1, 2, 4, 8]
const INITIAL_TIME = 0
const INITIAL_SPEED = 1
const CPU_PREVIEW: Array<ProcessorInfo & { accentColor: string }> = [
  {
    id: 'cpu-1',
    label: 'CPU 1',
    accentColor: '#38bdf8',
    status: 'executando',
    runningProcess: {
      id: 'P1',
      phase: 'fase_cpu_1',
      remainingCycles: 4,
      totalCycles: 10,
    },
  },
  {
    id: 'cpu-2',
    label: 'CPU 2',
    accentColor: '#22c55e',
    status: 'executando',
    runningProcess: {
      id: 'P2',
      phase: 'fase_cpu_2',
      remainingCycles: 2,
      totalCycles: 8,
    },
  },
  {
    id: 'cpu-3',
    label: 'CPU 3',
    accentColor: '#f59e0b',
    status: 'executando',
    runningProcess: {
      id: 'P3',
      phase: 'cpu_bound',
      remainingCycles: 5,
      totalCycles: 12,
    },
  },
  {
    id: 'cpu-4',
    label: 'CPU 4',
    accentColor: '#a78bfa',
    status: 'ociosa',
    runningProcess: null,
  },
]

const MEMORY_PREVIEW: MainMemoryInfo = {
  totalBlocks: 16,
  usedBlocks: 7,
  blocks: [
    { id: 'B1', occupied: true, processId: 'P1' },
    { id: 'B2', occupied: true, processId: 'P1' },
    { id: 'B3', occupied: true, processId: 'P2' },
    { id: 'B4', occupied: false, processId: null },
    { id: 'B5', occupied: true, processId: 'P3' },
    { id: 'B6', occupied: false, processId: null },
    { id: 'B7', occupied: false, processId: null },
    { id: 'B8', occupied: true, processId: 'P4' },
    { id: 'B9', occupied: true, processId: 'P5' },
    { id: 'B10', occupied: false, processId: null },
    { id: 'B11', occupied: false, processId: null },
    { id: 'B12', occupied: true, processId: 'P6' },
    { id: 'B13', occupied: false, processId: null },
    { id: 'B14', occupied: false, processId: null },
    { id: 'B15', occupied: false, processId: null },
    { id: 'B16', occupied: false, processId: null },
  ],
}

function App() {
  const [elapsedTime, setElapsedTime] = useState(INITIAL_TIME)
  const [isPaused, setIsPaused] = useState(false)
  const [speed, setSpeed] = useState(INITIAL_SPEED)

  useEffect(() => {
    if (isPaused) {
      return
    }

    const interval = window.setInterval(() => {
      setElapsedTime((currentTime) => currentTime + 1)
    }, 1000 / speed)

    return () => {
      window.clearInterval(interval)
    }
  }, [isPaused, speed])

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

  function handleReset() {
    setElapsedTime(INITIAL_TIME)
    setSpeed(INITIAL_SPEED)
    setIsPaused(true)
  }

  function handleStepBackward() {
    if (!isPaused) {
      return
    }

    setElapsedTime((currentTime) => Math.max(INITIAL_TIME, currentTime - 1))
  }

  function handleStepForward() {
    if (!isPaused) {
      return
    }

    setElapsedTime((currentTime) => currentTime + 1)
  }

  return (
    <main aria-label="Tela inicial do simulador" className="min-h-screen px-4 py-5">
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-6">
        <SimulationHeader
          elapsedTime={elapsedTime}
          isPaused={isPaused}
          speed={speed}
          canStepBackward={elapsedTime > INITIAL_TIME}
          onReset={handleReset}
          onStepBackward={handleStepBackward}
          onStepForward={handleStepForward}
          onTogglePause={handleTogglePause}
          onIncreaseSpeed={handleIncreaseSpeed}
        />

        <section className="flex w-full items-start gap-6">
          <div className="flex w-fit self-start gap-2 overflow-x-auto">
            {CPU_PREVIEW.map((cpu) => (
              <CpuCard
                key={cpu.id}
                cpu={cpu}
                accentColor={cpu.accentColor}
              />
            ))}
          </div>

          <div className="ml-auto">
            <MainMemoryPanel memory={MEMORY_PREVIEW} />
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
