import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildConfirmDialog,
  buildProfileStats,
  formatProfileDate,
  toProfileForm,
} from '../src/components/profile/profilePageModel.js'

test('creates profile form values from the current user', () => {
  assert.deepEqual(
    toProfileForm({
      id: 1,
      username: 'akira',
      nickname: '',
      bio: 'chat host',
      avatar_key: 'kanra',
      created_at: '2026-01-01T00:00:00Z',
    }),
    {
      nickname: 'akira',
      bio: 'chat host',
      avatarKey: 'kanra',
    },
  )
})

test('builds profile stats from owned rooms and account date', () => {
  const stats = buildProfileStats(
    [
      { peak_online_members: 5 },
      { peak_online_members: 7 },
      { peak_online_members: undefined },
    ],
    '2026-06-20T00:00:00Z',
    new Date('2026-06-24T00:00:00Z').getTime(),
  )

  assert.deepEqual(stats, [
    { label: '发布', value: 3 },
    { label: '评论', value: 12 },
    { label: '加入天数', value: 4 },
  ])
})

test('formats optional profile dates for display', () => {
  assert.equal(formatProfileDate(undefined), '-')
  assert.equal(formatProfileDate('2026-06-24T00:00:00Z'), '2026/06/24')
})

test('builds account action confirmation copy', () => {
  assert.equal(buildConfirmDialog(null, false), null)
  assert.deepEqual(buildConfirmDialog('delete', true), {
    title: '注销账号',
    description: '确定要注销当前账号吗？账号资料会被删除，此操作不可恢复。',
    confirmText: '注销中...',
    danger: true,
  })
})
