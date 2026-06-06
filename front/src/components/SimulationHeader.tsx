interface SimulationHeaderProps {
  elapsedTime: number
  isPaused: boolean
  speed: number
  canStepBackward: boolean
  onReset: () => void
  onStepBackward: () => void
  onStepForward: () => void
  onTogglePause: () => void
  onIncreaseSpeed: () => void
}

function formatTimeUnit(elapsedTime: number) {
  return elapsedTime.toString().padStart(2, '0')
}

function RestartIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5 fill-current">
      <rect x="5" y="5" width="14" height="14" rx="2" />
    </svg>
  )
}

function PauseIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5 fill-current">
      <rect x="6" y="5" width="4" height="14" rx="1.4" />
      <rect x="14" y="5" width="4" height="14" rx="1.4" />
    </svg>
  )
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5 fill-current">
      <path d="M8 5.5v13c0 .76.82 1.24 1.5.88l9.5-6.5a1.06 1.06 0 0 0 0-1.76L9.5 4.62A1 1 0 0 0 8 5.5Z" />
    </svg>
  )
}

function FastForwardIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4.5 w-4.5 fill-current">
      <path d="M4.5 6.3v11.4c0 .75.82 1.23 1.49.86L13 13.1c.62-.39.62-1.3 0-1.7L6 5.44a1 1 0 0 0-1.5.86Z" />
      <path d="M12.2 6.3v11.4c0 .75.82 1.23 1.49.86l7.01-5.46c.62-.39.62-1.3 0-1.7l-7.01-5.96a1 1 0 0 0-1.49.86Z" />
    </svg>
  )
}

function StepBackwardIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4.5 w-4.5 fill-current">
      <rect x="4" y="5.5" width="2.3" height="13" rx="0.6" />
      <path d="M18.8 6.3v11.4a1 1 0 0 1-1.49.86L10.3 14c-.62-.39-.62-1.3 0-1.7l7.01-5.96a1 1 0 0 1 1.49.86Z" />
    </svg>
  )
}

function StepForwardIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-4.5 w-4.5 fill-current">
      <path d="M5.2 6.3v11.4a1 1 0 0 0 1.49.86L13.7 14c.62-.39.62-1.3 0-1.7L6.69 6.34A1 1 0 0 0 5.2 7.2Z" />
      <rect x="17.7" y="5.5" width="2.3" height="13" rx="0.6" />
    </svg>
  )
}

export function SimulationHeader({
  elapsedTime,
  isPaused,
  speed,
  canStepBackward,
  onReset,
  onStepBackward,
  onStepForward,
  onTogglePause,
  onIncreaseSpeed,
}: SimulationHeaderProps) {
  return (
    <header className="inline-flex items-center gap-4 rounded-lg border border-white/10 bg-white/6 px-4 py-2.5 shadow-[0_24px_80px_rgba(0,0,0,0.28)] backdrop-blur-sm">
      <div className="space-y-1">
        <p className="text-[0.65rem] font-medium uppercase tracking-[0.28em] text-slate-400">
          Simulador
        </p>
        <div className="flex items-end gap-2">
          <span className="text-3xl font-semibold tracking-[-0.08em] text-white">
            {formatTimeUnit(elapsedTime)}
          </span>
          <span className="pb-0.5 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
            ut
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1.5 rounded-md border border-white/10 bg-black/20 p-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]">
        <button
          type="button"
          onClick={onReset}
          aria-label="Voltar ao inicio"
          title="Voltar ao inicio"
          className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/6 text-slate-200 transition hover:scale-[1.03] hover:bg-white/12 hover:text-white"
        >
          <RestartIcon />
        </button>

        <button
          type="button"
          onClick={onStepBackward}
          aria-label="Voltar 1 unidade de tempo"
          title="Voltar 1 ut"
          disabled={!isPaused || !canStepBackward}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/6 text-slate-200 transition hover:scale-[1.03] hover:bg-white/12 hover:text-white disabled:cursor-not-allowed disabled:border-white/6 disabled:bg-white/4 disabled:text-slate-500 disabled:hover:scale-100 disabled:hover:bg-white/4"
        >
          <StepBackwardIcon />
        </button>

        <button
          type="button"
          onClick={onTogglePause}
          aria-label={isPaused ? 'Retomar simulacao' : 'Pausar simulacao'}
          title={isPaused ? 'Retomar simulacao' : 'Pausar simulacao'}
          className="flex h-9 w-9 items-center justify-center rounded-md bg-white text-slate-950 shadow-[0_10px_30px_rgba(255,255,255,0.18)] transition hover:scale-[1.03]"
        >
          {isPaused ? <PlayIcon /> : <PauseIcon />}
        </button>

        <button
          type="button"
          onClick={onStepForward}
          aria-label="Avancar 1 unidade de tempo"
          title="Avancar 1 ut"
          disabled={!isPaused}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/6 text-slate-200 transition hover:scale-[1.03] hover:bg-white/12 hover:text-white disabled:cursor-not-allowed disabled:border-white/6 disabled:bg-white/4 disabled:text-slate-500 disabled:hover:scale-100 disabled:hover:bg-white/4"
        >
          <StepForwardIcon />
        </button>

        <button
          type="button"
          onClick={onIncreaseSpeed}
          aria-label={`Aumentar velocidade, atual ${speed}x`}
          title={`Velocidade atual ${speed}x`}
          className="flex h-8 min-w-18 items-center justify-center gap-1.5 rounded-md border border-sky-400/20 bg-sky-400/10 px-3 text-sky-100 transition hover:scale-[1.03] hover:bg-sky-400/16"
        >
          <FastForwardIcon />
          <span className="text-xs font-semibold tracking-[0.08em]">{speed}x</span>
        </button>
      </div>
    </header>
  )
}
