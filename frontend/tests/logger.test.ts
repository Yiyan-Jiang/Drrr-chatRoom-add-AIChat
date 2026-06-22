import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createLogger } from '../src/utils/logger.js'

type ConsoleMethod = 'debug' | 'info' | 'warn' | 'error'

function createConsoleSpy() {
  const calls: Array<{ method: ConsoleMethod; args: unknown[] }> = []

  return {
    calls,
    console: {
      debug: (...args: unknown[]) => calls.push({ method: 'debug', args }),
      info: (...args: unknown[]) => calls.push({ method: 'info', args }),
      warn: (...args: unknown[]) => calls.push({ method: 'warn', args }),
      error: (...args: unknown[]) => calls.push({ method: 'error', args }),
    },
  }
}

test('debug does not write to console when logs are disabled', () => {
  const spy = createConsoleSpy()
  const logger = createLogger({ isEnabled: () => false, console: spy.console })

  logger.debug('hidden message', { status: 200 })

  assert.deepEqual(spy.calls, [])
})

test('debug writes to console when logs are enabled', () => {
  const spy = createConsoleSpy()
  const logger = createLogger({ isEnabled: () => true, console: spy.console })

  logger.debug('visible message', { status: 200 })

  assert.deepEqual(spy.calls, [
    { method: 'debug', args: ['visible message', { status: 200 }] },
  ])
})

test('warn and error use the logger console sink even when debug logs are disabled', () => {
  const spy = createConsoleSpy()
  const logger = createLogger({ isEnabled: () => false, console: spy.console })
  const error = new Error('request failed')

  logger.warn('warning message')
  logger.error('error message', error)

  assert.equal(spy.calls.length, 2)
  assert.deepEqual(spy.calls[0], { method: 'warn', args: ['warning message'] })
  assert.equal(spy.calls[1]?.method, 'error')
  assert.equal(spy.calls[1]?.args[0], 'error message')
  assert.equal(spy.calls[1]?.args[1], error)
})
