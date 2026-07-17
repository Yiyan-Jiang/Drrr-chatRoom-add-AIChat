import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

function findFrontendRoot(start: string): string {
  let current = start
  for (let index = 0; index < 6; index += 1) {
    if (existsSync(resolve(current, 'src/contexts/AuthContext.tsx'))) {
      return current
    }
    if (existsSync(resolve(current, 'frontend/src/contexts/AuthContext.tsx'))) {
      return resolve(current, 'frontend')
    }
    current = resolve(current, '..')
  }
  throw new Error('Could not find frontend root')
}

const testDir = dirname(fileURLToPath(import.meta.url))
const frontendRoot = findFrontendRoot(testDir)
const authContextSource = readFileSync(resolve(frontendRoot, 'src/contexts/AuthContext.tsx'), 'utf8')
const apiClientSource = readFileSync(resolve(frontendRoot, 'src/api/client.ts'), 'utf8')

test('AuthContext validates stored token before opening the socket connection', () => {
  assert.match(
    authContextSource,
    /usersApi\.getMe\(\)/,
    'AuthContext should validate a stored token through the existing /users/me endpoint.',
  )

  assert.match(
    authContextSource,
    /socketManager\.connect\(token\)/,
    'AuthContext should still own the socket connection lifecycle.',
  )

  assert.ok(
    authContextSource.indexOf('usersApi.getMe()') < authContextSource.indexOf('socketManager.connect(token)'),
    'AuthContext should connect the socket only after token validation succeeds.',
  )
})

test('apiClient broadcasts auth expiration so AuthContext clears in-memory state', () => {
  assert.match(
    apiClientSource,
    /window\.dispatchEvent\(\s*new CustomEvent\('auth:unauthorized'\)/,
    '401 handling should notify AuthContext instead of only clearing localStorage.',
  )
})
