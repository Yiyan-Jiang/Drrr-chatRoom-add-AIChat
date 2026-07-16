import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const testDir = dirname(fileURLToPath(import.meta.url))
function findProjectRoot(start: string) {
  let current = start
  for (let depth = 0; depth < 5; depth += 1) {
    if (existsSync(resolve(current, 'src/routers/index.tsx'))) {
      return current
    }
    if (existsSync(resolve(current, 'frontend/src/routers/index.tsx'))) {
      return resolve(current, 'frontend')
    }
    current = resolve(current, '..')
  }
  throw new Error('Could not find frontend project root')
}

const projectRoot = findProjectRoot(testDir)
const loginSource = readFileSync(resolve(projectRoot, 'src/pages/auth/Login.tsx'), 'utf8')
const registerSource = readFileSync(resolve(projectRoot, 'src/pages/auth/Register.tsx'), 'utf8')
const routesSource = readFileSync(resolve(projectRoot, 'src/routers/index.tsx'), 'utf8')

test('auth pages rely on GateGuard instead of checking gate status themselves', () => {
  assert.match(routesSource, /element:\s*<GateGuard \/>/)
  assert.doesNotMatch(loginSource, /gateApi\.check/)
  assert.doesNotMatch(registerSource, /gateApi\.check/)
  assert.doesNotMatch(loginSource, /@\/api\/gate/)
  assert.doesNotMatch(registerSource, /@\/api\/gate/)
})
