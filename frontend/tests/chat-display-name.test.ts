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
const roomMemberSource = readFileSync(
  findFromParents(testDir, 'frontend/src/components/chat/RoomMemberList/RoomMemberList.tsx'),
  'utf8',
)
const roomInfoDrawerSource = readFileSync(
  findFromParents(testDir, 'frontend/src/components/chat/RoomInfoDrawer/RoomInfoDrawer.tsx'),
  'utf8',
)
const userDisplayNameSource = readFileSync(
  findFromParents(testDir, 'frontend/src/utils/userDisplayName.ts'),
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

test('Chat UI prefers nickname for user-facing display names', () => {
  assert.match(userDisplayNameSource, /nickname/)
  assert.match(chatMessageSource, /getUserDisplayName/)
  assert.match(roomMemberSource, /getUserDisplayName/)
  assert.match(roomInfoDrawerSource, /getUserDisplayName/)
  assert.doesNotMatch(chatMessageSource, /author\?\.username/)
  assert.doesNotMatch(roomMemberSource, /member\.username/)
})
