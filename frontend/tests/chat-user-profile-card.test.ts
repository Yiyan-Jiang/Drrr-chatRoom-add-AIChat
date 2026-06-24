import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, parse, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const chatMessageSource = readFileSync(
  findFromParents(testDir, 'frontend/src/components/chat/ChatMessageItem/ChatMessageItem.tsx'),
  'utf8',
)

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

test('chat message avatar opens a user profile card with core profile fields', () => {
  assert.match(chatMessageSource, /useState/)
  assert.match(chatMessageSource, /setProfileOpen/)
  assert.match(chatMessageSource, /aria-label="查看用户资料"/)
  assert.match(chatMessageSource, /role="dialog"/)
  assert.match(chatMessageSource, /author\.username/)
  assert.match(chatMessageSource, /author\.nickname/)
  assert.match(chatMessageSource, /author\.bio/)
  assert.match(chatMessageSource, /用户信息不可用/)
})
