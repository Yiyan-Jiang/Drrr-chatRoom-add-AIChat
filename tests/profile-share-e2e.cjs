/** 从登录和资料页面验证分享卡片及实际 PNG 下载。 */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright')
const assert = require('node:assert/strict')
const { randomUUID } = require('node:crypto')
const fs = require('node:fs/promises')
const api = 'http://localhost:8000/api'
let browser, context, user, headers
;(async () => {
  // Arrange（准备）：通过本机公开接口创建独立验收账号。
  await fs.mkdir('.tmp', { recursive: true })
  browser = await chromium.launch({
    executablePath: process.env.E2E_BROWSER_PATH,
    headless: true,
  })
  context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    acceptDownloads: true,
  })
  assert.equal(
    (
      await context.request.post(`${api}/gate/verify`, {
        form: { password: process.env.CHAT_GATE_PASSWORD },
      })
    ).status(),
    200,
  )
  const username = `card_${randomUUID().replaceAll('-', '')}${'x'.repeat(27)}`
  const password = randomUUID()
  const registered = await context.request.post(`${api}/users/register`, {
    data: { username, password },
  })
  assert.equal(registered.status(), 201)
  user = await registered.json()
  const login = await context.request.post(`${api}/auth/login`, {
    data: { username, password },
  })
  headers = { Authorization: `Bearer ${(await login.json()).access_token}` }
  const page = await context.newPage()
  page.setDefaultTimeout(12000)
  await page.goto('http://localhost:5173/login')
  await page.getByPlaceholder('Username', { exact: true }).fill(username)
  await page.getByPlaceholder('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'ENTER', exact: true }).click()
  await page.waitForURL('**/home/rooms')
  await page.goto('http://localhost:5173/my')
  await page.getByRole('button', { name: '编辑资料', exact: true }).click()
  await page.locator('input[maxlength="64"]').fill('夜行者')
  await page.locator('textarea').fill('在城市的另一端，与你相遇。')
  await page.getByRole('button', { name: '更换头像', exact: true }).click()
  await page.getByRole('button', { name: '头像 zawa', exact: true }).click()
  await page.getByRole('button', { name: '保存', exact: true }).click()
  await page.getByRole('button', { name: '编辑资料', exact: true }).waitFor()
  // Act（执行）：进入资料页，生成并下载卡片。
  await page.goto('http://localhost:5173/profile')
  assert.equal(
    await page.getByRole('button', { name: '编辑资料', exact: true }).count(),
    0,
  )
  await page.getByRole('button', { name: '生成分享卡片', exact: true }).click()
  const downloadEvent = page.waitForEvent('download')
  await page.getByRole('button', { name: '下载 PNG', exact: true }).click()
  const download = await downloadEvent
  await download.saveAs('.tmp/profile-card-export.png')
  // Assert（断言）：实际下载必须为完整尺寸的 PNG。
  const png = await fs.readFile('.tmp/profile-card-export.png')
  assert.equal(png.subarray(1, 4).toString(), 'PNG')
  assert.equal(png.readUInt32BE(16), 1536)
  assert.equal(png.readUInt32BE(20), 1024)
  const preview = page.getByRole('img', { name: /^会员分享卡片预览/ })
  const previewBytes = Buffer.from(
    (await preview.getAttribute('src')).split(',')[1],
    'base64',
  )
  assert.deepEqual(png, previewBytes)
  await page.screenshot({ path: '.tmp/profile-card-page.png', fullPage: true })
  // Assert（断言）：使用真实随机生成，覆盖六款底图并保存最终图片供视觉检查。
  const themes = new Set()
  for (let attempt = 0; attempt < 120 && themes.size < 6; attempt++) {
    await page
      .getByRole('button', { name: '生成分享卡片', exact: true })
      .click()
    await preview.waitFor()
    const theme = (await preview.getAttribute('alt')).split('：')[1]
    if (!themes.has(theme)) {
      await fs.writeFile(
        `.tmp/card-${theme}.png`,
        Buffer.from(
          (await preview.getAttribute('src')).split(',')[1],
          'base64',
        ),
      )
      themes.add(theme)
    }
  }
  assert.equal(themes.size, 6)
  await page.setViewportSize({ width: 375, height: 900 })
  const bounds = await preview.boundingBox()
  assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= 375)
  await page.screenshot({
    path: '.tmp/profile-card-mobile.png',
    fullPage: true,
  })
  // Act（执行）：通过“我的”编辑到允许的长度上限，检查新卡片同步资料。
  await page.setViewportSize({ width: 1440, height: 1100 })
  await page.goto('http://localhost:5173/my')
  await page.getByRole('button', { name: '编辑资料', exact: true }).click()
  await page.locator('input[maxlength="64"]').fill('夜行者'.repeat(21) + '终')
  await page
    .locator('textarea')
    .fill('城市另一端的朋友你好。'.repeat(18) + '终章')
  await page.getByRole('button', { name: '保存', exact: true }).click()
  await page.getByRole('button', { name: '编辑资料', exact: true }).waitFor()
  await page.goto('http://localhost:5173/profile')
  await preview.waitFor()
  const initialPreviewUrl = await preview.getAttribute('src')
  await fs.writeFile(
    '.tmp/profile-card-long.png',
    Buffer.from((await preview.getAttribute('src')).split(',')[1], 'base64'),
  )
  assert.notEqual(
    await preview.getAttribute('src'),
    `data:image/png;base64,${previewBytes.toString('base64')}`,
  )
  // Act（执行）：阻断图片网络边界，失败应可见，恢复后可重试。
  await page.route('**/profile-cards/*.png', (route) => route.abort())
  await page.getByRole('button', { name: '生成分享卡片', exact: true }).click()
  await page
    .getByRole('alert')
    .filter({ hasText: '分享卡片生成失败' })
    .waitFor()
  assert.equal(
    await page
      .getByRole('button', { name: '下载 PNG', exact: true })
      .isDisabled(),
    true,
  )
  assert.equal(await preview.count(), 0)
  await page.unroute('**/profile-cards/*.png')
  await page.getByRole('button', { name: '重试生成', exact: true }).click()
  await preview.waitFor()
  // Act（执行）：从公开资料接口保存允许的内部换行，重新登录状态读取后生成卡片。
  assert.equal(
    (
      await context.request.put(`${api}/users/me`, {
        headers,
        data: {
          nickname: 'A' + '\n'.repeat(62) + 'B',
          bio: '城市\n'.repeat(66) + '终章',
          avatar_key: 'zawa',
        },
      })
    ).status(),
    200,
  )
  await page.reload()
  await preview.waitFor()
  await page
    .locator('dd')
    .filter({ hasText: /^A B$/ })
    .waitFor({ state: 'attached' })
  await fs.writeFile(
    '.tmp/profile-card-newlines.png',
    Buffer.from((await preview.getAttribute('src')).split(',')[1], 'base64'),
  )
  assert.notEqual(await preview.getAttribute('src'), initialPreviewUrl)
  console.log(
    'PASS profile: edit in /my, no edit in /profile, six random backgrounds, PNG 1536x1024 equals preview, mobile width, max-length data, image error/retry',
  )
})()
  .catch((error) => {
    console.error(error)
    process.exitCode = 1
  })
  .finally(async () => {
    if (user && headers)
      assert.equal(
        (
          await context.request.delete(`${api}/users/${user.id}`, { headers })
        ).status(),
        204,
      )
    if (browser) await browser.close()
  })
