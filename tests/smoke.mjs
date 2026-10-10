import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { createRequire } from 'node:module'

// Reuse the application's Socket.IO client; no separate test dependencies.
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

function client() {
  return {
    cookie: '',
    token: '',
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
      // Avoid printing response bodies, which may contain tokens or passwords.
      assert.equal(
        response.status,
        status,
        `${method} ${route}: expected ${status}, got ${response.status}`,
      )
      return response.status === 204 ? undefined : response.json()
    },
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

async function join(socket, event, payload, historyEvent) {
  const history = waitForEvent(socket, historyEvent)
  socket.emit(event, payload)
  assert.ok(Array.isArray(await history), `${historyEvent} must return history`)
}

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

  const anonymous = client()
  await anonymous.request('GET', '/gate/status', undefined, 401)
  await anonymous.request('GET', '/users/me', undefined, 401)
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
  console.log('PASS gate cookie, registration, login and authenticated profile')

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
  const accepted = await bob.http.request(
    'POST',
    `/friends/requests/${request.id}/accept`,
  )
  assert.equal(accepted.status, 'accepted')
  const friends = await alice.http.request('GET', '/friends/')
  assert.ok(friends.items.some((item) => item.user.id === bob.id))
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
  await bob.http.request('DELETE', `/posts/${post.id}`, undefined, 403)
  await bob.http.request(
    'POST',
    `/posts/${post.id}/comments`,
    { content: 'smoke comment' },
    201,
  )
  await bob.http.request('PUT', `/posts/${post.id}/like`)
  await bob.http.request('PUT', `/posts/${post.id}/favorite`)
  const detail = await bob.http.request('GET', `/posts/${post.id}`)
  assert.equal(detail.content, 'smoke post body')
  assert.equal(detail.comments_count, 1)
  assert.equal(detail.likes_count, 1)
  assert.equal(detail.favorites_count, 1)
  assert.equal(detail.liked_by_me, true)
  assert.equal(detail.favorited_by_me, true)
  console.log('PASS post permissions, comments, likes and favorites')
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
