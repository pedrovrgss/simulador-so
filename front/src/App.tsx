import { useEffect, useState } from 'react'
import { CpuCard } from './components/CpuCard'
import { MainMemoryPanel } from './components/MainMemoryPanel'
import { SimulationHeader } from './components/SimulationHeader'
import { fallbackSnapshot } from './data/fallbackSnapshot'
import { SchedulingQueues } from './components/SchedulingQueues'
import { EventLog } from './components/EventLog'
import { DisksPanel } from './components/DisksPanel'
import type { ProcessorInfo } from './types/processor'

const SPEED_STEPS = [1, 2, 4, 8]
const INITIAL_TIME = 0
const INITIAL_SPEED = 1

const CPU_PREVIEW: Array<ProcessorInfo & { accentColor: string }> = [
  {
    id: 'cpu-1',
    label: 'CPU 1',
    accentColor: '#ff6b57',
    status: 'executando',
    runningProcess: {
      id: 'TR-01' as `P${number}`,
      phase: 'fase_cpu_1',
      remainingCycles: 4,
      totalCycles: 10,
    },
  },
  {
    id: 'cpu-2',
    label: 'CPU 2',
    accentColor: '#42d392',
    status: 'executando',
    runningProcess: {
      id: 'U-07' as `P${number}`,
      phase: 'fase_cpu_2',
      remainingCycles: 2,
      totalCycles: 8,
    },
  },
  {
    id: 'cpu-3',
    label: 'CPU 3',
    accentColor: '#5cc8ff',
    status: 'executando',
    runningProcess: {
      id: 'U-03' as `P${number}`,
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
    if (!isPaused) return
    setElapsedTime((currentTime) => Math.max(INITIAL_TIME, currentTime - 1))
  }

  function handleStepForward() {
    if (!isPaused) return
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

        <section className="flex w-full gap-4">
          <div className="flex flex-col gap-6" style={{ width: 'fit-content' }}>
            <div className="flex gap-2">
              {CPU_PREVIEW.map((cpu) => (
                <CpuCard key={cpu.id} cpu={cpu} accentColor={cpu.accentColor} />
              ))}
            </div>

            <div className="flex-1">
              <SchedulingQueues queues={fallbackSnapshot.queues} />
            </div>
          </div>

          <div className="flex flex-1 flex-col gap-4">
            <div style={{ height: '10.5rem' }}>
              <EventLog events={fallbackSnapshot.eventLog} />
            </div>
            <div className="flex-1">
              <DisksPanel disks={fallbackSnapshot.disks} />
            </div>
          </div>

          <div className="shrink-0">
            <MainMemoryPanel memory={fallbackSnapshot.memory} />
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
