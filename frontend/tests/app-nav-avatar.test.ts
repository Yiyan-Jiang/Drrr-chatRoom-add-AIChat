import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, parse, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const appNavPath = findFromParents(testDir, 'frontend/src/components/layout/AppNav/AppNav.tsx')
const appNavSource = readFileSync(appNavPath, 'utf8')

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

test('AppNav renders the current authenticated user avatar instead of text placeholder', () => {
  assert.match(appNavSource, /useAuth\(\)/)
  assert.match(appNavSource, /resolveChatAvatarAssets\(user\?\.avatar_key\)/)
  assert.match(appNavSource, /<img[^>]+src=\{avatarAssets\.avatar\}/)
  assert.doesNotMatch(appNavSource, /rounded-full/)
  assert.doesNotMatch(appNavSource, />\s*头像\s*</)
})
