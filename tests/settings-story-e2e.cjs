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
        .getByRole("heading", { name: /在这里，\s*总有人接住\s*你的下一句。/ })
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
      // Act（执行）：滚动阅读同一消息的三个阶段，通过键盘展开工程说明。
      await page.locator(".story-follow-message").click();
      for (const phase of [0, 1, 2]) {
        await page
          .locator(".story-passage")
          .nth(phase)
          .evaluate((el) =>
            el.scrollIntoView({ block: "center", behavior: "instant" }),
          );
        if (width > 900 && height >= 700 && reducedMotion !== "reduce") {
          await page.waitForFunction(
            (value) =>
              document.querySelector(".story-afterword").dataset.phase ===
              String(value),
            phase,
          );
        } else {
          assert.equal(
            await page
              .locator(".story-travelling-message")
              .evaluate((el) => getComputedStyle(el).position),
            "relative",
          );
          for (const status of await page
            .locator(".story-phase-status span")
            .all()) {
            assert.equal(
              await status.evaluate((el) => getComputedStyle(el).opacity),
              "1",
            );
          }
        }
      }
      await page.locator(".story-engineering summary").focus();
      await page.keyboard.press("Enter");
      await page
        .getByText(
          "数据库事务提交后才发送回执与房间广播。确认表示服务器已保存，不代表对方已读。",
          { exact: true },
        )
        .waitFor();
      await page.keyboard.press("Enter");
      assert.equal(
        await page.locator(".story-engineering").getAttribute("open"),
        null,
      );
      await page
        .locator("#message-journey")
        .evaluate((el) =>
          el.scrollIntoView({ block: "start", behavior: "instant" }),
        );
      await page.screenshot({
        path: ".tmp/visual-" + name + "-journey.png",
        animations: "disabled",
      });
      // Assert（断言）：完整介绍无技术代码块和剧集截图，交流入口保持真实目标。
      assert.deepEqual(
        await page
          .locator(".story-composer, .film-continuations a:not([target])")
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
      assert.deepEqual(images.slice(0, 2), [
        "/project-story/assets/drrr-keyvisual.jpg",
        "/project-story/assets/drrr-gathering.png",
      ]);
      assert.equal(await page.locator(".story-message").count(), 5);
      assert.equal(images.length, 7);
      assert.equal(
        images.some((src) => src.includes("chat-room.png")),
        false,
      );
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
        `PASS ${name}: posters/product decode, scroll story and details, keyboard/navigation, real links, no overflow or business requests`,
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
