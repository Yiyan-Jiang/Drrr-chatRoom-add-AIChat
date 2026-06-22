import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, parse, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const myPagePath = findFromParents(testDir, 'frontend/src/pages/subPage/MyPage.tsx')
const authContextPath = findFromParents(testDir, 'frontend/src/contexts/AuthContext.tsx')
const myPageSource = readFileSync(myPagePath, 'utf8')
const authContextSource = readFileSync(authContextPath, 'utf8')

function findFromParents(startDir: string, relativePath: string): string {
  let currentDir = startDir
  const root = parse(startDir).root

  while (true) {
    const candidate = resolve(currentDir, relativePath)
    if (existsSync(candidate)) {
      return candidate
    }
    if (currentDir === root) {
      throw new Error(`Unable to find ${relativePath} from ${startDir}`)
    }
    currentDir = resolve(currentDir, '..')
  }
}

test('MyPage loads and updates the current user profile only', () => {
  assert.match(myPageSource, /useAuth\(\)/)
  assert.match(myPageSource, /usersApi\.getMe/)
  assert.match(myPageSource, /usersApi\.updateMe/)
  assert.match(myPageSource, /roomApi\.listMine/)
  assert.match(myPageSource, /to=\{`\/chat\/\$\{room\.id\}`\}/)
  assert.match(myPageSource, /nickname/)
  assert.match(myPageSource, /bio/)
  assert.doesNotMatch(myPageSource, /password/)
  assert.doesNotMatch(myPageSource, /username.*setForm|setForm.*username/)
})

test('MyPage offers an avatar picker backed by the avatar catalog', () => {
  assert.match(myPageSource, /chatAvatarCatalog/)
  assert.match(myPageSource, /avatarKey/)
  assert.match(myPageSource, /avatar_key/)
})

test('AuthContext exposes a stable updateUser callback so profile load does not loop', () => {
  assert.match(authContextSource, /useCallback/)
  assert.match(authContextSource, /const updateUser = useCallback/)
})
