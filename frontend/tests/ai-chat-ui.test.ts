import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const projectRoot = resolve(testDir, '..', '..')
const aiChatSource = readFileSync(resolve(projectRoot, 'src/pages/room/AIChat.tsx'), 'utf8')
const aiChatHookSource = readFileSync(resolve(projectRoot, 'src/hooks/useAIchat.ts'), 'utf8')

test('AI chat page reuses normal chat room UI components', () => {
  assert.match(aiChatSource, /from '@\/components\/chat\/ChatRoomHeader'/)
  assert.match(aiChatSource, /from '@\/components\/chat\/ChatMessageViewport'/)

  assert.doesNotMatch(aiChatSource, /AIChatMessage/)
  assert.doesNotMatch(aiChatSource, /AILoadingIndicator/)
  assert.doesNotMatch(aiChatSource, /AIChatEmptyState/)
  assert.doesNotMatch(aiChatSource, /ChatMessageInput/)
  assert.doesNotMatch(aiChatSource, /from '@\/components\/chat\/ChatHeader'/)

  assert.equal(existsSync(resolve(projectRoot, 'src/components/AIchat/AIChatMessage')), false)
  assert.equal(existsSync(resolve(projectRoot, 'src/components/AIchat/AIChatEmptyState')), false)
})

test('AI chat exit returns to room list without logging out', () => {
  assert.doesNotMatch(aiChatSource, /\blogout\(\)/)
  assert.doesNotMatch(aiChatSource, /navigate\('\/login'\)/)
  assert.match(aiChatSource, /navigate\('\/home\/rooms'\)/)
})

test('AI chat page derives character and avatar state from URL and auth user', () => {
  assert.match(aiChatSource, /useSearchParams/)
  assert.match(aiChatSource, /useAuth\(\)/)
  assert.doesNotMatch(aiChatSource, /useState<AICharacter>\('sakura'\)/)
  assert.doesNotMatch(aiChatSource, /AICharacterTabs/)
})

test('AI chat prepends new messages to match the normal chat viewport order', () => {
  assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'user', content: userMessage \},\s*\n\s*\.\.\.prev/)
  assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'system', content: error \},\s*\n\s*\.\.\.prev/)
  assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'assistant', content: messages \},\s*\n\s*\.\.\.prev/)
  assert.match(aiChatSource, /const head = prev\[0\]/)
})

test('AI chat sends Sakura messages through the streaming agent turn endpoint', () => {
  assert.match(aiChatHookSource, /\/api\/ai\/turn\/stream/)
  assert.match(aiChatHookSource, /request_id/)
  assert.match(aiChatHookSource, /session_id/)
  assert.match(aiChatHookSource, /getReader\(\)/)
  assert.match(aiChatHookSource, /line\.startsWith\('event:'\)/)
  assert.match(aiChatHookSource, /currentEvent === 'session'/)
  assert.match(aiChatHookSource, /currentEvent === 'meta'/)
  assert.doesNotMatch(aiChatHookSource, /fetch\(`\$\{API_URL\}\/api\/ai\/chat`/)
  assert.doesNotMatch(aiChatHookSource, /fetch\(`\$\{API_URL\}\/api\/ai\/turn`,/)
})

test('AI chat renders streamed agent chunks without waiting for JSON answer', () => {
  assert.match(aiChatHookSource, /messageBufferRef/)
  assert.match(aiChatHookSource, /setMessages\(messageBufferRef\.current\)/)
  assert.doesNotMatch(
    aiChatHookSource,
    /setMessages\(payload\.answer \|\| ''\)/,
  )
})

test('AI chat hook loads paginated agent history for the selected character', () => {
  assert.match(aiChatHookSource, /\/api\/ai\/turn\/history\?/)
  assert.match(aiChatHookSource, /HISTORY_PAGE_SIZE = 30/)
  assert.match(aiChatHookSource, /limit: String\(HISTORY_PAGE_SIZE\)/)
  assert.match(aiChatHookSource, /before_sequence_no/)
  assert.match(aiChatHookSource, /loadOlderHistory/)
  assert.match(aiChatHookSource, /next_before_sequence_no/)
})

test('AI chat clear button deletes persisted history before clearing local state', () => {
  assert.match(aiChatHookSource, /method:\s*'DELETE'/)
  assert.match(aiChatHookSource, /\/api\/ai\/turn\/history\?character=/)
  assert.match(aiChatHookSource, /agentSessionIdRef\.current = null/)
})

test('AI chat page renders loaded history and wires older history pagination', () => {
  assert.match(aiChatSource, /historyItems/)
  assert.match(aiChatSource, /loadOlderHistory/)
  assert.match(aiChatSource, /hasMoreHistory/)
  assert.match(aiChatSource, /loadingOlderHistory/)
})
