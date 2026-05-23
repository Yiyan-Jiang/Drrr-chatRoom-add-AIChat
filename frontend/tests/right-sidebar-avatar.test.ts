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

test('RightSidebar resolves AI character avatar assets instead of rendering a placeholder', () => {
  assert.match(rightSidebarSource, /resolveChatAvatarAssets/)
  assert.match(rightSidebarSource, /avatarKey/)
  assert.match(rightSidebarSource, /<img[^>]+src=/)
  assert.doesNotMatch(rightSidebarSource, /\n\s*1\n/)
})
