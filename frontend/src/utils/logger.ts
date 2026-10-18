/** 提供按配置控制调试日志的控制台日志接口。 */
/** 日志输出所需的控制台方法集合。 */
type ConsoleLike = Pick<Console, 'debug' | 'info' | 'warn' | 'error'>

/** 日志开关与输出目标的注入选项。 */
type LoggerOptions = {
  /** 判断 debug 和 info 日志是否启用的回调。 */
  isEnabled?: () => boolean
  /** 接收日志的控制台实现。 */
  console?: ConsoleLike
}

/**
 * 只识别字符串 true 和 false，未提供或其他文本均返回 undefined。
 * @param value - 本地存储或环境变量中的日志开关文本。
 * @returns 识别出的布尔值，或 undefined。
 */
function parseBoolean(value: string | null | undefined): boolean | undefined {
  if (value === null || value === undefined) return undefined
  if (value === 'true') return true
  if (value === 'false') return false
  return undefined
}

/**
 * 优先读取本地日志开关，再读取环境日志开关；没有有效布尔配置时返回 false。
 * @returns debug 和 info 日志是否启用。
 */
function defaultIsEnabled(): boolean {
  const stored = parseBoolean(globalThis.localStorage?.getItem('debug_logs'))
  if (stored !== undefined) return stored

  const env = import.meta.env as {
    /** 优先读取的环境日志开关文本。 */
    VITE_DEBUG_LOGS?: string
    /** VITE_DEBUG_LOGS 未提供时读取的环境日志开关文本。 */
    VITE_APP_DEBUG_LOGS?: string
  }

  const fromEnv = parseBoolean(env.VITE_DEBUG_LOGS ?? env.VITE_APP_DEBUG_LOGS)
  return fromEnv ?? false
}

/**
 * 创建日志接口；debug 和 info 受开关控制，warn 和 error 始终输出。
 * @param options - 日志开关和控制台输出目标。
 * @returns 提供四个日志级别的接口。
 */
export function createLogger(options: LoggerOptions = {}) {
  const sink = options.console ?? globalThis.console
  const isEnabled = options.isEnabled ?? defaultIsEnabled

  return {
    /**
     * 日志开关启用时向输出目标写入 debug 日志。
     * @param args - 原样传递给控制台的日志参数。
     */
    debug: (...args: unknown[]) => {
      if (isEnabled()) sink.debug(...args)
    },
    /**
     * 日志开关启用时向输出目标写入 info 日志。
     * @param args - 原样传递给控制台的日志参数。
     */
    info: (...args: unknown[]) => {
      if (isEnabled()) sink.info(...args)
    },
    /**
     * 始终向输出目标写入 warn 日志。
     * @param args - 原样传递给控制台的日志参数。
     */
    warn: (...args: unknown[]) => {
      sink.warn(...args)
    },
    /**
     * 始终向输出目标写入 error 日志。
     * @param args - 原样传递给控制台的日志参数。
     */
    error: (...args: unknown[]) => {
      sink.error(...args)
    },
  }
}

/** 使用默认日志开关与全局控制台的共享日志实例。 */
export const logger = createLogger()
