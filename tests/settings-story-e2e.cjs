/** 从公开 React 入口验收海报、产品实景、消息演示、聊天入口和轻微视差。 */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const origin = process.env.STORY_ORIGIN || "http://127.0.0.1:5180";

(async () => {
  await fs.mkdir(".tmp", { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.E2E_BROWSER_PATH,
    headless: true,
  });
  try {
    for (const [name, width, height, reducedMotion] of [
      ["desktop", 1440, 1000, "no-preference"],
      ["mobile", 390, 844, "no-preference"],
      ["tablet", 820, 1180, "no-preference"],
      ["reduced", 1280, 900, "reduce"],
      ["short", 1280, 650, "no-preference"],
    ]) {
      // Arrange（准备）：仅放行本地页面与 Vite 热更新，隔离业务和外部连接。
      const context = await browser.newContext({
        viewport: { width, height },
        reducedMotion,
      });
      const blocked = [];
      await context.route("**/*", (route) => {
        const url = new URL(route.request().url());
        if (url.origin === origin && !/^\/(api|socket.io)\//.test(url.pathname))
          return route.continue();
        blocked.push(url.pathname);
        return route.abort();
      });
      await context.routeWebSocket(/.*/, (ws) => {
        const url = new URL(ws.url());
        if (url.origin === origin.replace("http", "ws") && url.pathname === "/")
          ws.connectToServer();
        else {
          blocked.push(url.pathname);
          ws.close();
        }
      });
      const page = await context.newPage();
      page.setDefaultTimeout(12000);
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      // Act（执行）：读取真实海报，在原生滚动中验证前景移动，再使用键盘导航。
      await page.goto(`${origin}/project-story`);
      await page.locator('.drrr-film[data-motion="ready"]').waitFor();
      await page
        .locator(".film-hero-poster img")
        .evaluate((img) => img.decode());
      await page.screenshot({
        path: `.tmp/poster-${name}-hero.png`,
        animations: "disabled",
      });
      const poster = page.locator(".film-hero-poster");
      const initialTransform = await poster.evaluate(
        (el) => getComputedStyle(el).transform,
      );
      await page.locator(".drrr-film").evaluate(async (el) => {
        el.scrollTop = 260;
        await new Promise((resolve) =>
          requestAnimationFrame(() => requestAnimationFrame(resolve)),
        );
      });
      if (width > 900 && height >= 700 && reducedMotion !== "reduce") {
        await page.waitForFunction(
          (previous) =>
            getComputedStyle(document.querySelector(".film-hero-poster"))
              .transform !== previous,
          initialTransform,
        );
      } else {
        assert.equal(
          await poster.evaluate((el) => getComputedStyle(el).transform),
          initialTransform,
          "小屏或减少动态模式不启用海报视差",
        );
      }
      await page.locator('.film-nav a[href="#origin"]').focus();
      await page.keyboard.press("Enter");
      await page.waitForFunction(
        () =>
          Math.abs(
            document.querySelector("#origin").getBoundingClientRect().top,
          ) < 100,
      );
      await page.locator(".film-gathering img").evaluate((img) => img.decode());
      await page.screenshot({
        path: `.tmp/poster-${name}-origin.png`,
        animations: "disabled",
      });
      await page
        .locator(".film-gathering")
        .evaluate((el) =>
          el.scrollIntoView({ block: "center", behavior: "instant" }),
        );
      await page.screenshot({
        path: `.tmp/poster-${name}-art.png`,
        animations: "disabled",
      });
      await page.locator('.film-nav a[href="#conversation"]').click();
      await page
        .getByRole("heading", { name: /从作品里的相遇，\s*到真正的聊天室。/ })
        .waitFor();
      assert.equal(
        await page
          .locator(".film-eyebrow, .film-opening-bottom, .film-demo-note")
          .count(),
        0,
      );
      await page.screenshot({
        path: `.tmp/poster-${name}-chat.png`,
        animations: "disabled",
      });
      for (const img of await page.locator(".drrr-film img").all()) {
        await img.evaluate((el) => el.decode());
        assert.equal(await img.evaluate((el) => el.naturalWidth > 0), true);
      }
      // Act（执行）：用键盘与点击查看消息阶段，展开实现说明。
      await page.locator(".film-product-caption a").click();
      await page.getByRole("button", { name: "确认", exact: true }).focus();
      await page.keyboard.press("Enter");
      assert.equal(
        (await page.locator(".film-message-receipt").innerText()).replace(
          /\s+/g,
          "",
        ),
        "✓已保存·已确认",
      );
      await page.getByText("看看背后的实现", { exact: false }).click();
      await page
        .getByText(
          "数据库事务提交后，Socket.IO 才发送确认与房间广播。确认代表服务器已保存，不代表对方已读。",
          { exact: true },
        )
        .waitFor();
      await page.getByRole("button", { name: "重连", exact: true }).click();
      assert.equal(
        (await page.locator(".film-message-receipt").innerText()).replace(
          /\s+/g,
          "",
        ),
        "✓历史已回补",
      );
      assert.equal(
        await page.locator(".film-engineering").getAttribute("open"),
        null,
      );
      await page.screenshot({
        path: ".tmp/product-" + name + "-journey.png",
        animations: "disabled",
      });
      await page.getByRole("button", { name: "发送", exact: true }).click();
      assert.equal(
        (await page.locator(".film-message-receipt").innerText()).replace(
          /\s+/g,
          "",
        ),
        "◌等待回执",
      );
      if (width <= 680) {
        await page.locator(".film-screen-scroll").evaluate((el) => {
          el.scrollLeft = el.scrollWidth;
        });
        assert.ok(
          await page
            .locator(".film-screen-scroll")
            .evaluate((el) => el.scrollLeft > 0),
          "小屏可横向查看产品界面",
        );
      }
      // Assert（断言）：完整介绍无技术代码块和剧集截图，交流入口保持真实目标。
      assert.deepEqual(
        await page
          .locator(".film-product-heading a, .film-continuations a")
          .evaluateAll((links) =>
            links.map((link) => link.getAttribute("href")),
          ),
        ["/home/rooms", "/friends", "/home/posts"],
      );
      assert.equal(
        await page.locator(".film-cta").getAttribute("href"),
        "/home/rooms",
      );
      assert.equal(await page.locator("pre").count(), 0);
      const images = await page
        .locator(".drrr-film img")
        .evaluateAll((imgs) => imgs.map((img) => img.getAttribute("src")));
      assert.deepEqual(images, [
        "/project-story/assets/drrr-keyvisual.jpg",
        "/project-story/assets/drrr-gathering.png",
        "/project-story/assets/chat-room.png",
        "/project-story/assets/avatar-kanra.png",
      ]);
      assert.equal(
        await page
          .locator(".drrr-film")
          .evaluate((el) => el.scrollWidth <= el.clientWidth),
        true,
      );
      await page.getByRole("link", { name: "回到开端 ↑", exact: true }).click();
      await page.waitForFunction(
        () => document.querySelector(".drrr-film").scrollTop < 10,
      );
      assert.deepEqual(errors, []);
      assert.deepEqual(blocked, []);
      console.log(
        `PASS ${name}: posters/product decode, message stages and details, keyboard/navigation, real links, no overflow or business requests`,
      );
      await context.close();
    }
    // Arrange（准备）：阻断可选动画模块，检查静态内容与入口仍然存在。
    const fallback = await browser.newContext();
    await fallback.route("**/*", (route) => {
      const url = new URL(route.request().url());
      if (/gsap|ScrollTrigger/.test(url.pathname)) return route.abort();
      return url.origin === origin ? route.continue() : route.abort();
    });
    const fallbackPage = await fallback.newPage();
    await fallbackPage.goto(`${origin}/project-story`);
    await fallbackPage
      .locator('.drrr-film[data-motion="unavailable"]')
      .waitFor();
    await fallbackPage.locator("#opening-title").waitFor();
    await fallbackPage.locator('.film-nav a[href="#origin"]').click();
    await fallbackPage.locator("#origin-title").waitFor();
    assert.equal(
      await fallbackPage
        .locator(".film-hero-poster img")
        .evaluate((img) => img.naturalWidth > 0),
      true,
    );
    console.log(
      "PASS animation load failure: poster, origin and navigation remain available",
    );
    await fallback.close();
    // Assert（断言）：禁用 JavaScript 后保留核心项目介绍与仓库链接。
    const noJs = await browser.newContext({ javaScriptEnabled: false });
    const page = await noJs.newPage();
    await page.goto(`${origin}/project-story`);
    await page
      .getByRole("heading", { name: "DOLLARS.", exact: true })
      .waitFor();
    assert.match(
      await page
        .getByRole("link", { name: "在 GitHub 探索项目 ↗" })
        .getAttribute("href"),
      /github.com/,
    );
    console.log("PASS no JavaScript fallback");
    await noJs.close();
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
