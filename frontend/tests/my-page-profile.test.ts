import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import { dirname, parse, resolve } from 'node:path'

const testDir = dirname(fileURLToPath(import.meta.url))
const myPagePath = findFromParents(testDir, 'frontend/src/pages/subPage/MyPage.tsx')
const authContextPath = findFromParents(testDir, 'frontend/src/contexts/AuthContext.tsx')
const postsApiPath = findFromParents(testDir, 'frontend/src/api/posts.ts')
const profileHeaderPath = findFromParents(testDir, 'frontend/src/components/profile/ProfileHeader.tsx')
const ownedRoomsPath = findFromParents(testDir, 'frontend/src/components/profile/OwnedRoomsSection.tsx')
const myPageSource = readFileSync(myPagePath, 'utf8')
const authContextSource = readFileSync(authContextPath, 'utf8')
const postsApiSource = readFileSync(postsApiPath, 'utf8')
const profileHeaderSource = readFileSync(profileHeaderPath, 'utf8')
const ownedRoomsSource = readFileSync(ownedRoomsPath, 'utf8')

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
  assert.match(myPageSource, /postsApi\.listMine/)
  assert.match(myPageSource, /postsApi\.listMyFavorites/)
  assert.match(myPageSource, /postsApi\.listMyComments/)
  assert.match(myPageSource, /postsApi\.listMyLikes/)
  assert.match(ownedRoomsSource, /to=\{`\/chat\/\$\{room\.id\}`\}/)
  assert.match(myPageSource, /nickname/)
  assert.match(myPageSource, /bio/)
  assert.doesNotMatch(myPageSource, /password/)
  assert.doesNotMatch(myPageSource, /username.*setForm|setForm.*username/)
})

test('posts API exposes current user comments for the profile page', () => {
  assert.match(postsApiSource, /interface PostCommentListItem/)
  assert.match(postsApiSource, /post_title: string/)
  assert.match(postsApiSource, /post_content_preview: string/)
  assert.match(postsApiSource, /listMine/)
  assert.match(postsApiSource, /\/posts\/mine/)
  assert.match(postsApiSource, /listMyComments/)
  assert.match(postsApiSource, /\/posts\/comments\/mine/)
  assert.match(postsApiSource, /listMyLikes/)
  assert.match(postsApiSource, /\/posts\/likes\/mine/)
})

test('MyPage renders post comment and favorite tabs from posts data', () => {
  assert.match(myPageSource, /activeTab/)
  assert.match(myPageSource, /myPosts/)
  assert.match(myPageSource, /favoritePosts/)
  assert.match(myPageSource, /likedPosts/)
  assert.match(myPageSource, /postComments/)
  assert.match(myPageSource, /<PostCard key=\{post\.id\} post=\{post\} \/>/)
  assert.match(myPageSource, /activeTab === 'posts'/)
  assert.match(myPageSource, /activeTab === 'likes'/)
  assert.match(myPageSource, /to=\{`\/posts\/\$\{comment\.post_id\}`\}/)
  assert.match(myPageSource, /comment\.post_title/)
})

test('MyPage offers an avatar picker backed by the avatar catalog', () => {
  assert.match(profileHeaderSource, /chatAvatarCatalog/)
  assert.match(profileHeaderSource, /avatarKey/)
  assert.match(profileHeaderSource, /avatar_key/)
})

test('MyPage shows selectable avatar previews in their original colors', () => {
  assert.match(profileHeaderSource, /className="h-12 w-12 object-cover"/)
  assert.doesNotMatch(profileHeaderSource, /className="h-12 w-12 object-cover grayscale"/)
})

test('MyPage shows the current avatar in full color as well', () => {
  assert.match(profileHeaderSource, /className="h-full w-full object-cover"/)
  assert.doesNotMatch(profileHeaderSource, /className="h-full w-full object-cover grayscale"/)
})

test('MyPage uses a Dollars-style profile route layout below the app header', () => {
  assert.match(myPageSource, /dollars-profile-shell/)
  assert.match(myPageSource, /dollars-profile-tabs/)
  assert.match(myPageSource, /最近访客/)
  assert.match(myPageSource, /个人资料/)
})

test('MyPage profile copy is Chinese and action buttons have content-friendly sizing', () => {
  const combinedSource = [myPageSource, profileHeaderSource, ownedRoomsSource].join('\n')
  assert.doesNotMatch(combinedSource, /[ぁ-んァ-ン]/)
  assert.doesNotMatch(profileHeaderSource, /grid-cols-2/)
  assert.doesNotMatch(profileHeaderSource, /lg:grid-cols-3/)
  assert.match(profileHeaderSource, /flex w-full flex-wrap/)
  assert.match(profileHeaderSource, /min-w-\[8rem\]/)
})

test('MyPage moves account actions into a compact more menu', () => {
  assert.match(profileHeaderSource, /account-actions-menu/)
  assert.match(profileHeaderSource, /更多账号操作/)
  assert.match(profileHeaderSource, /aria-label="关闭账号操作菜单"/)
  assert.match(profileHeaderSource, /onLogout\(\)/)
  assert.match(profileHeaderSource, /onDeleteAccount\(\)/)
})

test('MyPage separates the top profile summary from the lower content columns', () => {
  assert.match(myPageSource, /dollars-profile-topline/)
  assert.match(myPageSource, /justify-between/)
  assert.match(myPageSource, /dollars-profile-content-grid/)
  assert.doesNotMatch(myPageSource, /<section className="grid gap-7 lg:grid-cols-\[minmax\(0,1fr\)_390px\]"/)
})

test('AuthContext exposes a stable updateUser callback so profile load does not loop', () => {
  assert.match(authContextSource, /useCallback/)
  assert.match(authContextSource, /const updateUser = useCallback/)
})
