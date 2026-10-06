import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { test } from 'node:test'
import { runInNewContext } from 'node:vm'
import ts from 'typescript'

function loadModule(file, dependencies = {}) {
  const source = readFileSync(resolve('src', file), 'utf8')
  const code = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText
  const module = { exports: {} }
  runInNewContext(code, {
    module,
    exports: module.exports,
    require(name) {
      if (!(name in dependencies)) throw new Error(`Unexpected dependency: ${name}`)
      return dependencies[name]
    },
    crypto: { randomUUID: () => 'test-client-id' },
    window: { setTimeout: () => 1, clearTimeout() {} },
    Date, Map, Set,
  })
  return module.exports
}

const merge = loadModule('hooks/chatMessageMerge.ts')
const history = loadModule('hooks/chatHistory.ts', { './chatMessageMerge': merge })

function message(id, extra = {}) {
  return { id, room_id: 1, user_id: 1, content: `message ${id}`, created_at: new Date(id * 1000).toISOString(), ...extra }
}

function page(items, hasMore = true, cursor = items.at(-1)?.id ?? null) {
  return { items, has_more: hasMore, next_before_id: cursor }
}

// Exercise the real hook callbacks and reducers without a browser or new dependencies.
// React rendering itself remains covered by build/lint, not by this callback harness.
function chatHarness(privateChat, seed, getPage) {
  let state
  const effects = []
  const refs = []
  let refIndex = 0
  const handlers = new Map()
  const socketManager = new Proxy({}, {
    get(_target, name) {
      if (name.startsWith('on')) return (callback) => handlers.set(name, callback)
      if (name.startsWith('off')) return () => handlers.delete(name.replace('off', 'on'))
      return () => {}
    },
  })
  const react = {
    useReducer(reducer, initial) {
      state ??= { ...initial, ...seed }
      return [state, (action) => { state = reducer(state, action) }]
    },
    useState(initial) { return [initial, () => {}] },
    useRef(current) {
      const index = refIndex++
      refs[index] ??= current === state ? { get current() { return state } } : { current }
      return refs[index]
    },
    useEffect(effect) { effects.push(effect) },
    useCallback(callback) { return callback },
  }
  const dependencies = {
    react,
    axios: { isAxiosError: () => false },
    'react-hot-toast': { default: { success() {} } },
    '@/api/rooms': { roomApi: { getById: async (id) => ({ id }) } },
    '@/api/messages': { messagesApi: { getPageByRoom: getPage } },
    '@/api/users': { usersApi: { getById: async (id) => ({ id }) } },
    '@/api/privateMessages': { privateMessagesApi: { getPageByFriend: getPage } },
    '@/services/socket': { socketManager },
    '@/utils/logger': { logger: { error() {} } },
    './chatMessageMerge': merge,
    './chatHistory': history,
  }
  const file = privateChat ? 'hooks/usePrivateChat.ts' : 'hooks/useRoomChat.ts'
  const exported = loadModule(file, dependencies)
  const hook = privateChat ? exported.usePrivateChat : exported.useRoomChat
  const actions = hook(privateChat ? 2 : 1, { id: 1 }, () => true, () => {})
  return {
    actions,
    snapshot: () => state,
    subscribe: () => effects.at(-1)(),
    startInitial: () => effects.at(-2)(),
    event: (name, payload) => handlers.get(name)?.(payload),
    rerender(id) {
      effects.length = 0
      refIndex = 0
      return hook(id, { id: 1 }, () => true, () => {})
    },
  }
}

async function settleCallbacks() {
  for (let i = 0; i < 40; i++) await Promise.resolve()
}

for (const privateChat of [false, true]) {
  const label = privateChat ? 'private chat' : 'room chat'
  const seed = { messages: [message(10)], hasMore: true, nextBeforeId: 10 }

  test(`${label}: history failure preserves the cursor and allows a retry`, async () => {
    const harness = chatHarness(privateChat, seed, async () => { throw new Error('offline') })
    await harness.actions.loadOlderMessages()
    assert.equal(harness.snapshot().loadingOlder, false)
    assert.equal(harness.snapshot().hasMore, true)
    assert.equal(harness.snapshot().nextBeforeId, 10)
    assert.equal(harness.snapshot().messages[0].id, 10)
  })

  test(`${label}: reconnect recovers a gap larger than one page without discarding history`, async () => {
    const requests = []
    const harness = chatHarness(privateChat, seed, async (_id, options) => {
      requests.push(options.beforeId ?? null)
      const raw = options.beforeId ? [message(11), message(10)] : [message(13), message(12)]
      const items = privateChat ? raw.map((item) => ({ ...item, sender_id: 2, recipient_id: 1 })) : raw
      return page(items)
    })
    harness.subscribe()
    harness.event('onReconnect')
    await settleCallbacks()
    assert.deepEqual(requests, [null, 12])
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [13, 12, 11, 10])
    assert.equal(harness.snapshot().nextBeforeId, 10)
  })

  test(`${label}: messages for another conversation are ignored`, () => {
    const harness = chatHarness(privateChat, seed, async () => page([]))
    harness.subscribe()
    harness.event(privateChat ? 'onPrivateNewMessage' : 'onNewMessage',
      privateChat ? { ...message(11), sender_id: 3, recipient_id: 1 } : message(11, { room_id: 2 }))
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [10])
  })

  test(`${label}: an in-flight reconnect cannot update a chat after cleanup`, async () => {
    let resolvePage
    const harness = chatHarness(privateChat, seed, () => new Promise((resolve) => { resolvePage = resolve }))
    const cleanup = harness.subscribe()
    harness.event('onReconnect')
    cleanup()
    resolvePage(page([message(11)]))
    await settleCallbacks()
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [10])
  })

  test(`${label}: a failed second recovery page does not commit a partial gap`, async () => {
    let fail = true
    const harness = chatHarness(privateChat, seed, async (_id, options) => {
      if (options.beforeId && fail) throw new Error('offline during recovery')
      const raw = options.beforeId ? [message(11), message(10)] : [message(13), message(12)]
      return page(privateChat ? raw.map((item) => ({ ...item, sender_id: 2, recipient_id: 1 })) : raw)
    })
    harness.subscribe()
    harness.event('onReconnect')
    await settleCallbacks()
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [10])
    fail = false
    harness.event('onDisconnect')
    harness.event('onReconnect')
    await settleCallbacks()
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [13, 12, 11, 10])
  })

  test(`${label}: disconnect invalidates a previous recovery request`, async () => {
    let resolvePage
    const harness = chatHarness(privateChat, seed, () => new Promise((resolve) => { resolvePage = resolve }))
    harness.subscribe()
    harness.event('onReconnect')
    harness.event('onDisconnect')
    resolvePage(page([message(11), message(10)]))
    await settleCallbacks()
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [10])
  })

  test(`${label}: initial history does not overwrite a message received while loading`, async () => {
    let resolvePage
    const harness = chatHarness(privateChat, seed, () => new Promise((resolve) => { resolvePage = resolve }))
    harness.startInitial()
    await settleCallbacks()
    harness.subscribe()
    harness.event(privateChat ? 'onPrivateNewMessage' : 'onNewMessage',
      privateChat ? { ...message(11), sender_id: 2, recipient_id: 1 } : message(11))
    resolvePage(page([message(10)]))
    await settleCallbacks()
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [11, 10])
  })

  test(`${label}: live traffic after failed recovery does not move the missing-history watermark`, async () => {
    let fail = true
    const requests = []
    const harness = chatHarness(privateChat, seed, async (_id, options) => {
      requests.push(options.beforeId ?? null)
      if (options.beforeId && fail) throw new Error('offline during recovery')
      const raw = options.beforeId ? [message(11), message(10)] : [message(13), message(12)]
      return page(privateChat ? raw.map((item) => ({ ...item, sender_id: 2, recipient_id: 1 })) : raw)
    })
    harness.subscribe()
    harness.event('onDisconnect')
    harness.event('onReconnect')
    await settleCallbacks()
    harness.event(privateChat ? 'onPrivateNewMessage' : 'onNewMessage',
      privateChat ? { ...message(14), sender_id: 2, recipient_id: 1 } : message(14))
    fail = false
    requests.length = 0
    harness.event('onDisconnect')
    harness.event('onReconnect')
    await settleCallbacks()
    assert.deepEqual(requests, [null, 12])
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [14, 13, 12, 11, 10])
  })

  test(`${label}: an older-history response is ignored after the chat is left`, async () => {
    let calls = 0
    let resolvePage
    const harness = chatHarness(privateChat, seed, async () => {
      if (++calls === 1) return page([message(10)])
      return new Promise((resolve) => { resolvePage = resolve })
    })
    const cleanup = harness.startInitial()
    await settleCallbacks()
    const pending = harness.actions.loadOlderMessages()
    cleanup()
    resolvePage(page([message(9)]))
    await pending
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [10])
  })

  test(`${label}: a queued old history callback cannot use the new conversation scope`, async () => {
    const requests = []
    const harness = chatHarness(privateChat, seed, async (id) => {
      requests.push(id)
      return page([message(id === 3 ? 30 : 10)])
    })
    const oldCallback = harness.actions.loadOlderMessages
    const cleanup = harness.startInitial()
    await settleCallbacks()
    cleanup()
    harness.rerender(3)
    harness.startInitial()
    await settleCallbacks()
    const requestCount = requests.length
    await oldCallback()
    assert.equal(requests.length, requestCount)
    assert.deepEqual(Array.from(harness.snapshot().messages, (item) => item.id), [30])
  })
}

test('message merge removes duplicate IDs within an incoming history batch', () => {
  const result = merge.mergeMessages([], [message(1), message(1)], 'head')
  assert.equal(result.length, 1)
})

test('an empty recovered history closes pagination without an invalid cursor', () => {
  const result = history.mergeRecoveredHistory({ messages: [], hasMore: true, nextBeforeId: null }, page([], false, null))
  assert.equal(result.hasMore, false)
  assert.equal(result.nextBeforeId, null)
})

test('recovery reaching the beginning of history clears the old cursor', () => {
  const result = history.mergeRecoveredHistory({ messages: [message(10)], hasMore: true, nextBeforeId: 10 }, page([message(1)], false, null))
  assert.equal(result.hasMore, false)
  assert.equal(result.nextBeforeId, null)
})

test('recovery exceeding the view cap keeps an accessible cursor for evicted history', () => {
  const result = history.mergeRecoveredHistory({ messages: [message(1)], hasMore: false, nextBeforeId: null }, page(Array.from({ length: 310 }, (_, index) => message(index + 2)), false, null))
  assert.equal(result.messages.length, 300)
  assert.equal(result.hasMore, true)
  assert.equal(result.nextBeforeId, 12)
})
