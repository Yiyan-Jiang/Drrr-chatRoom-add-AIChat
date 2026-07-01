import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const projectRoot = existsSync(resolve(testDir, '..', 'src'))
  ? resolve(testDir, '..')
  : resolve(testDir, '..', 'frontend')
const srcRoot = resolve(projectRoot, 'src')

function readSource(path: string) {
  return readFileSync(resolve(srcRoot, path), 'utf8')
}

test('friend and private message APIs are exported', () => {
  assert.ok(existsSync(resolve(srcRoot, 'api/friends.ts')))
  assert.ok(existsSync(resolve(srcRoot, 'api/privateMessages.ts')))

  const apiIndex = readSource('api/index.ts')
  assert.match(apiIndex, /export \* from '\.\/friends'/)
  assert.match(apiIndex, /export \* from '\.\/privateMessages'/)

  const friendsApi = readSource('api/friends.ts')
  assert.match(friendsApi, /listFriends/)
  assert.match(friendsApi, /createRequest/)
  assert.match(friendsApi, /acceptRequest/)
  assert.match(friendsApi, /rejectRequest/)
  assert.match(friendsApi, /cancelRequest/)
  assert.match(friendsApi, /deleteFriend/)
  assert.doesNotMatch(friendsApi, /message:/)

  const privateMessagesApi = readSource('api/privateMessages.ts')
  assert.match(privateMessagesApi, /getPageByFriend/)
})

test('socket manager wraps private chat events', () => {
  const socketManager = readSource('services/socket/socketManager.ts')

  assert.match(socketManager, /joinPrivateChat/)
  assert.match(socketManager, /leavePrivateChat/)
  assert.match(socketManager, /sendPrivateMessage/)
  assert.match(socketManager, /onPrivateMessageAck/)
  assert.match(socketManager, /onPrivateNewMessage/)
  assert.match(socketManager, /onPrivateChatError/)
  assert.match(socketManager, /join_private_chat/)
  assert.match(socketManager, /private_message_ack/)
})

test('private chat hook, page, and route exist', () => {
  assert.ok(existsSync(resolve(srcRoot, 'hooks/usePrivateChat.ts')))
  assert.ok(existsSync(resolve(srcRoot, 'pages/room/PrivateChat.tsx')))

  const hook = readSource('hooks/usePrivateChat.ts')
  assert.match(hook, /usePrivateChat/)
  assert.match(hook, /createOptimisticMessage/)
  assert.match(hook, /joinPrivateChat/)
  assert.match(hook, /sendPrivateMessage/)

  const page = readSource('pages/room/PrivateChat.tsx')
  assert.match(page, /ChatMessageViewport/)
  assert.match(page, /ChatRoomHeader/)
  assert.match(page, /usePrivateChat/)

  const router = readSource('routers/index.tsx')
  assert.match(router, /PrivateChat/)
  assert.match(router, /private-chat\/:friendId/)
})
