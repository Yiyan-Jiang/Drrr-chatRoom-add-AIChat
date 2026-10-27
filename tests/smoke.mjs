/** 通过真实 HTTP 和 Socket.IO 入口验证主要业务链路，并清理本次临时数据。 */
import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { createRequire } from 'node:module'

// 复用应用已有的 Socket.IO 客户端，不引入独立测试依赖。
const { io } = createRequire(
  new URL('../frontend/package.json', import.meta.url),
)('socket.io-client')
const apiUrl = process.env.SMOKE_API_URL || 'http://127.0.0.1:8000'
const webUrl = process.env.SMOKE_WEB_URL || 'http://127.0.0.1:5173'
const gatePassword = process.env.CHAT_GATE_PASSWORD
const timeout = 10000
const runId = randomUUID().replaceAll('-', '')
const password = randomUUID()
const cleanup = []
const sockets = []

if (process.argv.includes('--help')) {
  console.log(
    'Usage: npm run test:smoke\nRequires running frontend, backend and migrated MySQL.\nCHAT_GATE_PASSWORD: gate password (loaded from backend/.env if present)\nSMOKE_API_URL: backend origin (default http://127.0.0.1:8000)\nSMOKE_WEB_URL: frontend origin (default http://127.0.0.1:5173)',
  )
  process.exit(0)
}

/**
 * 使用统一超时访问公开地址，连接失败时补充目标地址的诊断。
 * @param url - 前端入口或后端公开接口地址。
 * @param options - 传递给 fetch 的请求选项。
 * @returns 原始 HTTP 响应，由调用方核对状态和正文。
 */
async function fetchWithTimeout(url, options = {}) {
  try {
    return await fetch(url, {
      ...options,
      signal: AbortSignal.timeout(timeout),
    })
  } catch {
    throw new Error(
      `Cannot reach ${url} within ${timeout}ms; check service startup and addresses`,
    )
  }
}

/** 创建独立保存门禁 Cookie 和访问令牌的 HTTP 会话。 */
function client() {
  return {
    cookie: '',
    token: '',
    /**
     * 核对状态码，读取 JSON 业务数据或服务端的纯文本错误。
     * @param method - HTTP 方法。
     * @param route - 相对于 /api 的业务路径。
     * @param body - 可选 JSON 请求体。
     * @param status - 期望的 HTTP 状态码。
     * @returns 解析后的正文；204 响应返回 undefined。
     */
    async request(method, route, body, status = 200) {
      const headers = {}
      if (this.cookie) headers.Cookie = this.cookie
      if (this.token) headers.Authorization = `Bearer ${this.token}`
      if (body !== undefined) headers['Content-Type'] = 'application/json'
      const response = await fetchWithTimeout(`${apiUrl}/api${route}`, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
      })
      // 响应可能包含令牌或密码，断言失败时只输出状态信息。
      assert.equal(
        response.status,
        status,
        `${method} ${route}: expected ${status}, got ${response.status}`,
      )
      if (response.status === 204) return undefined
      return response.headers.get('content-type')?.includes('application/json')
        ? response.json()
        : response.text()
    },
    /** 通过真实门禁接口取得 Cookie，并读回验证状态。 */
    async passGate() {
      const response = await fetchWithTimeout(`${apiUrl}/api/gate/verify`, {
        method: 'POST',
        body: new URLSearchParams({ password: gatePassword }),
      })
      assert.equal(
        response.status,
        200,
        'Gate verification failed; check CHAT_GATE_PASSWORD',
      )
      this.cookie = response.headers
        .getSetCookie()
        .find((value) => value.startsWith('gate_passed='))
        ?.split(';')[0]
      assert.ok(this.cookie, 'Gate did not issue a cookie')
      assert.equal((await this.request('GET', '/gate/status')).verified, true)
    },
  }
}

/** 登录本次临时账号，并核对用户 ID 和密码字段隔离。 */
async function login(account) {
  const result = await account.http.request('POST', '/auth/login', {
    username: account.username,
    password,
  })
  assert.ok(result.access_token, 'Login did not issue a token')
  account.http.token = result.access_token
  assert.equal(result.user.id, account.id)
  assert.ok(!('password' in result.user), 'Login exposed a password')
}

/** 创建并登录唯一临时账号，同时登记账号清理动作。 */
async function register(suffix) {
  const http = client()
  await http.passGate()
  const username = `smoke_${runId}_${suffix}`
  const user = await http.request(
    'POST',
    '/users/register',
    { username, password },
    201,
  )
  const account = { http, username, id: user.id }
  cleanup.push({
    name: `user ${username} (${user.id})`,
    run: async () => {
      if (!http.token) await login(account)
      await http.request('DELETE', `/users/${user.id}`, undefined, 204)
      await http.request('GET', `/users/${user.id}`, undefined, 404)
    },
  })
  await login(account)
  assert.equal((await http.request('GET', '/users/me')).id, user.id)
  assert.ok(!('password' in user), 'Registration exposed a password')
  return account
}

/**
 * 等待符合条件的 Socket 事件，结束时移除监听和超时计时器。
 * @param socket - 当前测试场景的独立 Socket 客户端。
 * @param event - 要等待的服务端事件名。
 * @param matches - 匹配本次业务数据的条件；不匹配的事件继续等待。
 * @returns 首个匹配事件的载荷；超时、连接错误或断开时拒绝。
 */
function waitForEvent(socket, event, matches = () => true) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(
      () => finish(new Error(`Socket event ${event} timed out`)),
      timeout,
    )
    function finish(error, value) {
      clearTimeout(timer)
      socket.off(event, onEvent)
      socket.off('connect_error', onError)
      socket.off('disconnect', onDisconnect)
      error ? reject(error) : resolve(value)
    }
    function onEvent(value) {
      if (matches(value)) finish(null, value)
    }
    function onError() {
      finish(new Error(`Socket connection failed while waiting for ${event}`))
    }
    function onDisconnect() {
      finish(new Error(`Socket disconnected while waiting for ${event}`))
    }
    socket.on(event, onEvent)
    socket.on('connect_error', onError)
    socket.on('disconnect', onDisconnect)
  })
}

/** 为临时账号创建独立 Socket 连接，并登记最终断开操作。 */
async function connect(account) {
  const socket = io(apiUrl, {
    auth: { token: account.http.token },
    autoConnect: false,
    reconnection: false,
    forceNew: true,
    timeout,
  })
  sockets.push(socket)
  const connected = waitForEvent(socket, 'connect')
  socket.connect()
  await connected
  return socket
}

/** 加入群聊或私聊，以历史响应事件确认加入链路完成。 */
async function join(socket, event, payload, historyEvent) {
  const history = waitForEvent(socket, historyEvent)
  socket.emit(event, payload)
  assert.ok(Array.isArray(await history), `${historyEvent} must return history`)
}

/**
 * 发送消息并同时核对发送方确认、另一客户端投递和持久化消息 ID。
 * @param sender - 发送消息的 Socket 客户端。
 * @param receiver - 应接收消息的另一独立客户端。
 * @param event - 发送消息使用的服务端事件名。
 * @param payload - 包含唯一客户端消息标识的消息载荷。
 * @param ackEvent - 发送方应收到的确认事件。
 * @param newEvent - 接收方应收到的消息事件。
 * @returns 发送方收到的已持久化消息。
 */
async function send(sender, receiver, event, payload, ackEvent, newEvent) {
  const matches = (message) =>
    message?.client_message_id === payload.client_message_id
  const received = Promise.all([
    waitForEvent(sender, ackEvent, matches),
    waitForEvent(receiver, newEvent, matches),
  ])
  sender.emit(event, payload)
  const [ack, delivered] = await received
  assert.ok(
    Number.isInteger(ack.id) && ack.id > 0,
    'Message ack must contain a persisted ID',
  )
  assert.equal(ack.id, delivered.id)
  assert.equal(delivered.content, payload.content)
  return ack
}

/** 顺序验证页面入口、门禁账号、群聊、好友私聊和帖子互动。 */
async function smoke() {
  assert.ok(
    gatePassword,
    'Set CHAT_GATE_PASSWORD or configure backend/.env before running smoke',
  )
  const web = await fetchWithTimeout(webUrl)
  assert.equal(web.status, 200, 'Frontend is unavailable')
  const html = await web.text()
  assert.match(html, /id=["']root["']/)
  const entry = [
    ...html.matchAll(/<script[^>]*src=["']([^"']+)["'][^>]*>/g),
  ].at(-1)?.[1]
  assert.ok(entry, 'Frontend did not serve a script entry')
  const script = await fetchWithTimeout(new URL(entry, webUrl))
  assert.equal(script.status, 200, 'Frontend script entry is unavailable')
  console.log(
    'PASS frontend HTML and script availability (browser rendering is checked manually)',
  )

  // Given（前置）：建立匿名会话，准备两个独立的临时账号。
  const anonymous = client()
  await anonymous.request('GET', '/gate/status', undefined, 401)
  await anonymous.request('GET', '/users/me', undefined, 401)
  // When（操作）：通过门禁、注册和登录，并尝试未通过门禁及错误密码登录。
  const alice = await register('a')
  await anonymous.request(
    'POST',
    '/auth/login',
    { username: alice.username, password },
    401,
  )
  const bob = await register('b')
  await bob.http.request(
    'POST',
    '/auth/login',
    { username: bob.username, password: `${password}_wrong` },
    401,
  )
  // Then（结果）：公开入口返回预期状态，登录资料不含密码。
  console.log('PASS gate cookie, registration, login and authenticated profile')

  // Given（前置）：由一个账号创建房间，并登记房间清理动作。
  const room = await alice.http.request(
    'POST',
    '/rooms/',
    { name: `s${runId.slice(0, 7)}` },
    201,
  )
  cleanup.push({
    name: `room ${room.id}`,
    run: async () => {
      await alice.http.request('DELETE', `/rooms/${room.id}`, undefined, 204)
      await alice.http.request('GET', `/rooms/${room.id}`, undefined, 404)
    },
  })
  await bob.http.request(
    'PATCH',
    `/rooms/${room.id}`,
    { notice: 'denied' },
    403,
  )
  // When（操作）：两个账号加入同一房间，实时发送消息并通过 HTTP 重放。
  const aliceSocket = await connect(alice)
  const bobSocket = await connect(bob)
  await join(
    aliceSocket,
    'join_room',
    { room_id: room.id },
    'previous_messages',
  )
  await join(bobSocket, 'join_room', { room_id: room.id }, 'previous_messages')
  const roomPayload = {
    room_id: room.id,
    content: `group smoke ${runId}`,
    client_message_id: `room_${runId}`,
  }
  const roomMessage = await send(
    aliceSocket,
    bobSocket,
    'send_message',
    roomPayload,
    'message_ack',
    'new_message',
  )
  assert.equal(roomMessage.user_id, alice.id)
  assert.equal(roomMessage.room_id, room.id)
  const retry = await alice.http.request('POST', '/messages/', roomPayload, 201)
  assert.equal(
    retry.id,
    roomMessage.id,
    'Retry created a duplicate group message',
  )
  // Then（结果）：另一账号能够读回正文，重放没有产生重复消息。
  const history = await bob.http.request(
    'GET',
    `/messages/room/${room.id}/page`,
  )
  assert.equal(
    history.items.filter(
      (item) => item.client_message_id === roomPayload.client_message_id,
    ).length,
    1,
  )
  assert.equal(
    history.items.find((item) => item.id === roomMessage.id)?.content,
    roomPayload.content,
  )
  console.log(
    'PASS room permissions, two-client group delivery, persistence and retry',
  )

  // Given（前置）：准备普通消息、无关用户和另一房间，所有资源沿用 finally 清理。
  const unrelated = await register('unrelated')
  const ownMessage = await bob.http.request('POST', '/messages/', {
    room_id: room.id,
    content: `permission_own_${runId}`,
  }, 201)
  // When（操作）：匿名和无关用户尝试删除，作者随后删除自己的普通消息。
  await anonymous.request('DELETE', `/messages/${ownMessage.id}`, undefined, 401)
  await unrelated.http.request('DELETE', `/messages/${ownMessage.id}`, undefined, 403)
  const otherRoom = await unrelated.http.request('POST', '/rooms/', {
    name: `p${runId.slice(0, 7)}`,
  }, 201)
  cleanup.push({
    name: `room ${otherRoom.id}`,
    run: async () => {
      await unrelated.http.request('DELETE', `/rooms/${otherRoom.id}`, undefined, 204)
      await unrelated.http.request('GET', `/rooms/${otherRoom.id}`, undefined, 404)
    },
  })
  await unrelated.http.request('DELETE', `/messages/${ownMessage.id}`, undefined, 403)
  assert.equal((await alice.http.request('GET', `/messages/${ownMessage.id}`)).content, ownMessage.content)
  await bob.http.request('DELETE', `/messages/${ownMessage.id}`, undefined, 204)
  await alice.http.request('GET', `/messages/${ownMessage.id}`, undefined, 404)
  await bob.http.request('DELETE', `/messages/${ownMessage.id}`, undefined, 404)

  // Then（结果）：所属房主可管理他人普通消息，作者和房主都不能删除系统消息。
  const moderatedMessage = await bob.http.request('POST', '/messages/', {
    room_id: room.id,
    content: `permission_owner_${runId}`,
  }, 201)
  await alice.http.request('DELETE', `/messages/${moderatedMessage.id}`, undefined, 204)
  await bob.http.request('GET', `/messages/${moderatedMessage.id}`, undefined, 404)
  const systemHistory = await alice.http.request('GET', `/messages/room/${room.id}/page?limit=30`)
  const systemMessage = systemHistory.items.find((item) => item.message_type === 'system' && item.user_id === bob.id)
  assert.ok(systemMessage, '真实入房事件必须生成系统消息')
  await bob.http.request('DELETE', `/messages/${systemMessage.id}`, undefined, 403)
  await alice.http.request('DELETE', `/messages/${systemMessage.id}`, undefined, 403)
  assert.equal((await alice.http.request('GET', `/messages/${systemMessage.id}`)).message_type, 'system')

  // Given（前置）：通过真实注销流程将普通消息的作者关联置空。
  const departed = await register('departed')
  const orphanMessage = await departed.http.request('POST', '/messages/', {
    room_id: room.id,
    content: `permission_orphan_${runId}`,
  }, 201)
  await departed.http.request('DELETE', `/users/${departed.id}`, undefined, 204)
  cleanup.pop()
  // When（操作）：无关用户与所属房主分别尝试管理注销作者留下的消息。
  assert.equal((await alice.http.request('GET', `/messages/${orphanMessage.id}`)).user_id, null)
  await unrelated.http.request('DELETE', `/messages/${orphanMessage.id}`, undefined, 403)
  await alice.http.request('DELETE', `/messages/${orphanMessage.id}`, undefined, 204)
  // Then（结果）：注销作者的普通消息由所属房主删除，删除结果可读回确认。
  await alice.http.request('GET', `/messages/${orphanMessage.id}`, undefined, 404)
  console.log('PASS message author, owning-room moderation, system protection and deleted-author scope')


  // Given（前置）：先确认非好友无法加入私聊，再提交好友申请。
  const deniedPrivateChat = waitForEvent(aliceSocket, 'private_chat_error')
  aliceSocket.emit('join_private_chat', { friend_id: bob.id })
  assert.equal(
    (await deniedPrivateChat).message,
    'Only friends can join private chat',
  )
  const request = await alice.http.request(
    'POST',
    '/friends/requests',
    { recipient_id: bob.id },
    201,
  )
  // When（操作）：另一账号接受申请，双方加入私聊并发送消息。
  const accepted = await bob.http.request(
    'POST',
    `/friends/requests/${request.id}/accept`,
  )
  assert.equal(accepted.status, 'accepted')
  const friends = await alice.http.request('GET', '/friends/')
  assert.ok(friends.items.some((item) => item.user.id === bob.id))
  // When（操作）：按用户名和昵称搜索，核对通配符按字面匹配且不返回非好友。
  await bob.http.request('PUT', '/users/me', {
    nickname: `好友_${runId.slice(0, 8)}_%`,
  })
  for (const search of [
    bob.username.toUpperCase(),
    `好友_${runId.slice(0, 8)}`,
    '%',
  ]) {
    const matched = await alice.http.request(
      'GET',
      `/friends/?search=${encodeURIComponent(search)}&page=1&page_size=1`,
    )
    assert.equal(matched.total, 1)
    assert.equal(matched.items[0].user.id, bob.id)
    assert.equal(matched.has_more, false)
  }
  for (const search of [`no_match_${runId}`, alice.username]) {
    const empty = await alice.http.request(
      'GET',
      `/friends/?search=${encodeURIComponent(search)}`,
    )
    // Then（结果）：无匹配或搜索非好友时，记录与总数都为空。
    assert.deepEqual(empty.items, [])
    assert.equal(empty.total, 0)
    assert.equal(empty.has_more, false)
  }
  const restoredFriends = await alice.http.request(
    'GET',
    '/friends/?search=%20%20',
  )
  assert.equal(restoredFriends.total, friends.total)
  console.log('PASS friend search, literal keywords, scope and cleared results')
  await join(
    aliceSocket,
    'join_private_chat',
    { friend_id: bob.id },
    'private_previous_messages',
  )
  await join(
    bobSocket,
    'join_private_chat',
    { friend_id: alice.id },
    'private_previous_messages',
  )
  const privatePayload = {
    recipient_id: bob.id,
    content: `private smoke ${runId}`,
    client_message_id: `private_${runId}`,
  }
  const privateMessage = await send(
    aliceSocket,
    bobSocket,
    'send_private_message',
    privatePayload,
    'private_message_ack',
    'private_new_message',
  )
  assert.equal(privateMessage.sender_id, alice.id)
  assert.equal(privateMessage.recipient_id, bob.id)
  // Then（结果）：私聊收到确认及实时投递，且可通过历史接口读回。
  const privateHistory = await bob.http.request(
    'GET',
    `/private-messages/${alice.id}`,
  )
  assert.equal(
    privateHistory.items.find((item) => item.id === privateMessage.id)?.content,
    privatePayload.content,
  )
  console.log(
    'PASS friend request, acceptance, two-client private delivery and persistence',
  )

  // Arrange（准备）：消息已持久化，读取历史不会自动清除未读。
  await anonymous.request(
    'GET',
    '/private-messages/conversations',
    undefined,
    401,
  )
  let inbox = await bob.http.request(
    'GET',
    '/private-messages/conversations?page_size=1',
  )
  assert.equal(inbox.items[0].user.id, alice.id)
  assert.equal(inbox.items[0].latest_message.id, privateMessage.id)
  assert.equal(inbox.items[0].unread_count, 1)
  assert.equal(inbox.has_more, false)
  const senderInbox = await alice.http.request(
    'GET',
    '/private-messages/conversations',
  )
  assert.equal(senderInbox.items[0].unread_count, 0)
  // Act（执行）：从已显示消息边界标记已读，拒绝不属于接收者的边界。
  await alice.http.request(
    'PUT',
    `/private-messages/${bob.id}/read`,
    { through_id: privateMessage.id },
    404,
  )
  await bob.http.request(
    'PUT',
    `/private-messages/${alice.id}/read`,
    { through_id: privateMessage.id },
    204,
  )
  await login(bob)
  inbox = await bob.http.request('GET', '/private-messages/conversations')
  assert.equal(inbox.items[0].unread_count, 0)
  const changed = waitForEvent(bobSocket, 'mailbox_changed')
  const secondMessage = await send(
    aliceSocket,
    bobSocket,
    'send_private_message',
    {
      ...privatePayload,
      content: '新的未读消息',
      client_message_id: `second_${runId}`,
    },
    'private_message_ack',
    'private_new_message',
  )
  await changed
  await bob.http.request(
    'PUT',
    `/private-messages/${alice.id}/read`,
    { through_id: privateMessage.id },
    204,
  )
  // Assert（断言）：较旧的已读请求不覆盖新消息，重新登录后状态仍正确。
  inbox = await bob.http.request('GET', '/private-messages/conversations')
  assert.equal(inbox.items[0].latest_message.id, secondMessage.id)
  assert.equal(inbox.items[0].unread_count, 1)
  await bob.http.request(
    'PUT',
    `/private-messages/${alice.id}/read`,
    { through_id: secondMessage.id },
    204,
  )
  await bob.http.request('PUT', '/users/me', {
    nickname: '资料验收',
    bio: '冒烟测试简介',
    avatar_key: 'gray',
  })
  await login(bob)
  const savedProfile = await bob.http.request('GET', '/users/me')
  assert.equal(savedProfile.nickname, '资料验收')
  assert.equal(savedProfile.bio, '冒烟测试简介')
  assert.equal(savedProfile.avatar_key, 'gray')
  console.log(
    'PASS mailbox scope, unread persistence, read boundary and profile changes',
  )

  // Arrange（准备）：第三个账号只与 Alice 建立会话，用于验证分页和隔离。
  const carol = await register('c')
  // Given（前置）：Carol 从未加入群聊，另建仅通过门禁但未登录的会话。
  const gateOnly = client()
  await gateOnly.passGate()
  // When（操作）：分别以匿名、仅门禁和登录身份访问用户、房间及消息查询入口。
  await anonymous.request('GET', '/users/count', undefined, 401)
  const userCount = await gateOnly.request('GET', '/users/count')
  assert.ok(Number.isInteger(userCount.total) && userCount.total >= 3)
  const queryRoutes = [
    `/users/${alice.id}`,
    `/users/username/${alice.username}`,
    '/rooms/',
    '/rooms/mine',
    '/rooms/viewers/count',
    `/rooms/name/${room.name}`,
    `/rooms/${room.id}`,
    `/messages/room/${room.id}`,
    `/messages/room/${room.id}/page`,
    `/messages/${roomMessage.id}`,
  ]
  for (const route of queryRoutes) {
    await anonymous.request('GET', route, undefined, 401)
    await gateOnly.request('GET', route, undefined, 401)
  }
  // Then（结果）：登录用户无需加入房间即可读取公开资料和历史，响应保留业务内容。
  assert.equal((await carol.http.request('GET', queryRoutes[0])).id, alice.id)
  assert.equal((await carol.http.request('GET', queryRoutes[1])).id, alice.id)
  assert.ok(Array.isArray(await carol.http.request('GET', '/rooms/')))
  assert.deepEqual(await carol.http.request('GET', '/rooms/mine'), [])
  assert.ok(
    Number.isInteger(
      (await carol.http.request('GET', '/rooms/viewers/count')).total,
    ),
  )
  assert.equal(
    (await carol.http.request('GET', `/rooms/name/${room.name}`)).id,
    room.id,
  )
  const publicRoom = await carol.http.request('GET', `/rooms/${room.id}`)
  assert.equal(publicRoom.id, room.id)
  assert.ok(publicRoom.messages.some((item) => item.id === roomMessage.id))
  const publicHistory = await carol.http.request(
    'GET',
    `/messages/room/${room.id}`,
  )
  assert.ok(publicHistory.some((item) => item.id === roomMessage.id))
  const publicPage = await carol.http.request(
    'GET',
    `/messages/room/${room.id}/page`,
  )
  assert.ok(publicPage.items.some((item) => item.id === roomMessage.id))
  assert.equal(
    (await carol.http.request('GET', `/messages/${roomMessage.id}`)).content,
    roomPayload.content,
  )
  console.log('PASS query authentication, gate-only count and public room history')
  assert.deepEqual(
    (await carol.http.request('GET', '/private-messages/conversations')).items,
    [],
  )
  await carol.http.request(
    'PUT',
    `/private-messages/${alice.id}/read`,
    { through_id: privateMessage.id },
    404,
  )
  const carolRequest = await alice.http.request(
    'POST',
    '/friends/requests',
    { recipient_id: carol.id },
    201,
  )
  await carol.http.request(
    'POST',
    `/friends/requests/${carolRequest.id}/accept`,
  )
  const carolSocket = await connect(carol)
  // Act（执行）：接收方未加入私聊频道时仍应收到邮箱刷新事件。
  const carolChanged = waitForEvent(carolSocket, 'mailbox_changed')
  const carolAck = waitForEvent(
    aliceSocket,
    'private_message_ack',
    (message) => message.client_message_id === `carol_${runId}`,
  )
  aliceSocket.emit('send_private_message', {
    recipient_id: carol.id,
    content: '分页会话',
    client_message_id: `carol_${runId}`,
  })
  await Promise.all([carolChanged, carolAck])
  // Assert（断言）：最新会话排在首位，第二页正确，Bob 无法看到第三人的会话。
  const firstInboxPage = await alice.http.request(
    'GET',
    '/private-messages/conversations?page_size=1',
  )
  assert.equal(firstInboxPage.items[0].user.id, carol.id)
  assert.equal(firstInboxPage.has_more, true)
  const secondInboxPage = await alice.http.request(
    'GET',
    '/private-messages/conversations?page_size=1&page=2',
  )
  assert.equal(secondInboxPage.items[0].user.id, bob.id)
  assert.equal(secondInboxPage.has_more, false)
  assert.equal(
    (await bob.http.request('GET', '/private-messages/conversations')).items
      .length,
    1,
  )
  console.log(
    'PASS mailbox sorting, pagination, isolation and delivery outside private chat',
  )

  // Given（前置）：发布临时帖子，并登记帖子清理动作。
  const post = await alice.http.request(
    'POST',
    '/posts/',
    { title: `smoke ${runId}`, content: 'smoke post body' },
    201,
  )
  cleanup.push({
    name: `post ${post.id}`,
    run: async () => {
      await alice.http.request('DELETE', `/posts/${post.id}`, undefined, 204)
      await alice.http.request('GET', `/posts/${post.id}`, undefined, 404)
    },
  })
  // When（操作）：验证非作者删除被拒绝，并提交评论、点赞和收藏。
  await bob.http.request('DELETE', `/posts/${post.id}`, undefined, 403)
  await bob.http.request(
    'POST',
    `/posts/${post.id}/comments`,
    { content: 'smoke comment' },
    201,
  )
  await bob.http.request('PUT', `/posts/${post.id}/like`)
  await bob.http.request('PUT', `/posts/${post.id}/favorite`)
  // Then（结果）：正文、互动计数和当前用户状态均可读回。
  const detail = await bob.http.request('GET', `/posts/${post.id}`)
  assert.equal(detail.content, 'smoke post body')
  assert.equal(detail.comments_count, 1)
  assert.equal(detail.likes_count, 1)
  assert.equal(detail.favorites_count, 1)
  assert.equal(detail.liked_by_me, true)
  assert.equal(detail.favorited_by_me, true)
  console.log('PASS post permissions, comments, likes and favorites')

  // Arrange（准备）：Alice 与 Bob、Carol 为好友，Bob 和 Carol 互非好友。
  assert.deepEqual(
    (await alice.http.request('GET', '/posts/?friends_only=true')).items,
    [],
  )
  const friendPost = await bob.http.request(
    'POST',
    '/posts/',
    { title: '好友帖子', content: '好友动态验收' },
    201,
  )
  cleanup.push({
    name: `post ${friendPost.id}`,
    run: () =>
      bob.http.request('DELETE', `/posts/${friendPost.id}`, undefined, 204),
  })
  const newerPost = await carol.http.request(
    'POST',
    '/posts/',
    { title: '较新好友帖子', content: '分页验收' },
    201,
  )
  cleanup.push({
    name: `post ${newerPost.id}`,
    run: () =>
      carol.http.request('DELETE', `/posts/${newerPost.id}`, undefined, 204),
  })
  // Act（执行）：通过真实好友范围查询浏览最新与下一页帖子。
  const friendFeed = await alice.http.request(
    'GET',
    '/posts/?friends_only=true&limit=1',
  )
  assert.equal(friendFeed.items[0].id, newerPost.id)
  assert.equal(friendFeed.has_more, true)
  const friendNext = await alice.http.request(
    'GET',
    `/posts/?friends_only=true&limit=1&cursor=${friendFeed.next_cursor}`,
  )
  assert.equal(friendNext.items[0].id, friendPost.id)
  assert.equal(friendNext.has_more, false)
  // Assert（断言）：自己的帖子和非好友帖子不进入好友动态，普通帖子列表保持可见。
  const bobFeed = await bob.http.request('GET', '/posts/?friends_only=true')
  assert.deepEqual(
    bobFeed.items.map((item) => item.id),
    [post.id],
  )
  assert.ok(
    (await bob.http.request('GET', '/posts/')).items.some(
      (item) => item.id === newerPost.id,
    ),
  )
  console.log(
    'PASS friends-only posts, newest-first pagination and author scope',
  )

  // Given（前置）：删除第三个临时账号，保留其尚未过期的令牌触发真实外键错误。
  const removed = await register('removed')
  await removed.http.request('DELETE', `/users/${removed.id}`, undefined, 204)
  await removed.http.request('GET', `/users/${removed.id}`, undefined, 404)
  cleanup.pop()

  // When（操作）：通过公开接口为现有帖子写入无有效账号归属的互动。
  // Then（结果）：完整性错误必须返回失败，不能被当作已点赞或已收藏处理。
  await removed.http.request('PUT', `/posts/${post.id}/like`, undefined, 500)
  await removed.http.request(
    'PUT',
    `/posts/${post.id}/favorite`,
    undefined,
    500,
  )
  const unchangedPost = await bob.http.request('GET', `/posts/${post.id}`)
  assert.equal(unchangedPost.likes_count, 1)
  assert.equal(unchangedPost.favorites_count, 1)
  console.log('PASS post integrity failures remain observable')
}

try {
  await smoke()
} catch (error) {
  console.error(`FAIL ${error.message}`)
  process.exitCode = 1
} finally {
  for (const socket of sockets) socket.disconnect()
  for (const task of cleanup.reverse()) {
    try {
      await task.run()
    } catch (error) {
      console.error(`FAIL cleanup ${task.name}: ${error.message}`)
      process.exitCode = 1
    }
  }
}
if (!process.exitCode)
  console.log('PASS smoke completed and test resources removed')
