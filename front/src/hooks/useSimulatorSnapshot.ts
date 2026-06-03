import { useEffect, useState } from 'react'
import type { SimulatorSnapshot } from '../types/simulator'

interface SnapshotState {
  snapshot: SimulatorSnapshot
  source: 'api' | 'fallback'
  error: string | null
}

const API_URL = 'http://localhost:8000/api/snapshot'

export function useSimulatorSnapshot(fallback: SimulatorSnapshot): SnapshotState {
  const [state, setState] = useState<SnapshotState>({
    snapshot: fallback,
    source: 'fallback',
    error: null,
  })

  useEffect(() => {
    let active = true

    async function loadSnapshot() {
      try {
        const response = await fetch(API_URL)

        if (!response.ok) {
          throw new Error(`Falha HTTP ${response.status}`)
        }

        const snapshot = (await response.json()) as SimulatorSnapshot

        if (!active) {
          return
        }

        setState({
          snapshot,
          source: 'api',
          error: null,
        })
      } catch (error) {
        if (!active) {
          return
        }

        setState({
          snapshot: fallback,
          source: 'fallback',
          error: error instanceof Error ? error.message : 'Falha desconhecida',
        })
      }
    }

    void loadSnapshot()

    return () => {
      active = false
    }
  }, [fallback])

  return state
}
