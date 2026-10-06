import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(testDir, '..', '..')
const rightSidebarSource = readFileSync(
  resolve(projectRoot, 'src/components/layout/RightSidebar/RightSidebar.tsx'),
  'utf8',
)

test('RightSidebar resolves friend avatars and private chat links', () => {
  assert.match(rightSidebarSource, /resolveChatAvatarAssets/)
  assert.match(rightSidebarSource, /friend\.user\.avatar_key/)
  assert.match(rightSidebarSource, /\/private-chat\/\$\{friend\.user\.id\}/)
  assert.match(rightSidebarSource, /<img[^>]+src=/)
  assert.doesNotMatch(rightSidebarSource, /\n\s*1\n/)
  assert.doesNotMatch(rightSidebarSource, /\/ai-chat|AI_CHARACTERS/)
})
