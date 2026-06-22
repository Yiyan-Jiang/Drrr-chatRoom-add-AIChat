type ConsoleLike = Pick<Console, 'debug' | 'info' | 'warn' | 'error'>

type LoggerOptions = {
  isEnabled?: () => boolean
  console?: ConsoleLike
}

function parseBoolean(value: string | null | undefined): boolean | undefined {
  if (value === null || value === undefined) return undefined
  if (value === 'true') return true
  if (value === 'false') return false
  return undefined
}

function defaultIsEnabled(): boolean {
  const stored = parseBoolean(globalThis.localStorage?.getItem('debug_logs'))
  if (stored !== undefined) return stored

  const env = import.meta.env as {
    VITE_DEBUG_LOGS?: string
    VITE_APP_DEBUG_LOGS?: string
  }

  const fromEnv = parseBoolean(env.VITE_DEBUG_LOGS ?? env.VITE_APP_DEBUG_LOGS)
  return fromEnv ?? false
}

export function createLogger(options: LoggerOptions = {}) {
  const sink = options.console ?? globalThis.console
  const isEnabled = options.isEnabled ?? defaultIsEnabled

  return {
    debug: (...args: unknown[]) => {
      if (isEnabled()) sink.debug(...args)
    },
    info: (...args: unknown[]) => {
      if (isEnabled()) sink.info(...args)
    },
    warn: (...args: unknown[]) => {
      sink.warn(...args)
    },
    error: (...args: unknown[]) => {
      sink.error(...args)
    },
  }
}

export const logger = createLogger()
