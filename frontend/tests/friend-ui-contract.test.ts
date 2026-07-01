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

test('shared UserHoverCard handles friend actions without request message input', () => {
  assert.ok(existsSync(resolve(srcRoot, 'components/user/UserHoverCard.tsx')))
  const source = readSource('components/user/UserHoverCard.tsx')

  assert.match(source, /friendsApi\.createRequest/)
  assert.match(source, /friendsApi\.listFriends/)
  assert.match(source, /friendsApi\.listRequests/)
  assert.match(source, /\/private-chat\/\$\{user\.id\}/)
  assert.doesNotMatch(source, /textarea/)
  assert.doesNotMatch(source, /createRequest\(\{[^}]*message:/s)
})

test('chat and every post avatar surface use UserHoverCard', () => {
  const chatMessage = readSource('components/chat/ChatMessageItem/ChatMessageItem.tsx')
  const postAvatar = readSource('components/posts/PostAuthorAvatar.tsx')
  const postCard = readSource('components/posts/PostCard.tsx')
  const postDetail = readSource('pages/subPage/PostDetail.tsx')
  const commentList = readSource('components/posts/CommentList.tsx')

  assert.match(chatMessage, /UserHoverCard/)
  assert.match(postAvatar, /UserHoverCard/)
  assert.match(postCard, /PostAuthorAvatar author=\{post\.author\}/)
  assert.match(postDetail, /PostAuthorAvatar author=\{post\.author\}/)
  assert.match(commentList, /PostAuthorAvatar author=\{comment\.author\}/)
})

test('MyPage settings tab loads and processes friend requests', () => {
  const source = readSource('pages/subPage/MyPage.tsx')

  assert.match(source, /friendsApi\.listRequests/)
  assert.match(source, /filterPendingFriendRequests/)
  assert.match(source, /friendsApi\.acceptRequest/)
  assert.match(source, /friendsApi\.rejectRequest/)
  assert.match(source, /friendsApi\.cancelRequest/)
  assert.match(source, /incomingFriendRequests/)
  assert.match(source, /outgoingFriendRequests/)
})

test('RightSidebar appends paginated friends below the four AI entries', () => {
  const source = readSource('components/layout/RightSidebar/RightSidebar.tsx')

  assert.match(source, /friendsApi\.listFriends/)
  assert.match(source, /friendPage/)
  assert.match(source, /pageSize/)
  assert.match(source, /hasMoreFriends/)
  assert.match(source, /\/private-chat\/\$\{friend\.user\.id\}/)
  assert.match(source, /flex h-\[80%\] flex-col/)
  assert.match(source, /min-h-0 flex-1 overflow-y-auto/)
  assert.match(source, /grid auto-rows-\[90px\]/)
  assert.match(source, /h-\[90px\]/)
  assert.match(source, /mt-auto/)
  assert.match(source, /AI_CHARACTERS\.map/)
  assert.match(source, /friends\.map/)
})

test('FriendsPage renders the real friend list and request queues', () => {
  const source = readSource('pages/subPage/FriendsPage.tsx')

  assert.match(source, /friendsApi\.listFriends/)
  assert.match(source, /friendsApi\.listRequests/)
  assert.match(source, /filterPendingFriendRequests/)
  assert.match(source, /friendsApi\.acceptRequest/)
  assert.match(source, /friendsApi\.rejectRequest/)
  assert.match(source, /friendsApi\.cancelRequest/)
  assert.match(source, /friendsApi\.deleteFriend/)
  assert.match(source, /navigate\(`\/private-chat\/\$\{friend\.user\.id\}`\)/)
  assert.match(source, /incomingFriendRequests/)
  assert.match(source, /outgoingFriendRequests/)
})

test('package exposes targeted friend contract test script', () => {
  const packageJson = readFileSync(resolve(projectRoot, 'package.json'), 'utf8')

  assert.match(packageJson, /test:friend-private-chat/)
  assert.match(packageJson, /private-chat-contract\.test\.ts/)
  assert.match(packageJson, /friend-ui-contract\.test\.ts/)
})
