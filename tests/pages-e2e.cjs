/** 从实际静态产物验收仓库子路径、资源加载、导航和业务隔离。 */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const { once } = require("node:events");
const base = "/Drrr-chatRoom-add-AIChat/";
const output = path.resolve(__dirname, "../dist/pages");
const repo = "https://github.com/Yiyan-Jiang/Drrr-chatRoom-add-AIChat";

(async () => {
  // Arrange（准备）：只提供实际构建文件，不使用 SPA 回退，也不连接业务服务。
  await fs.access(path.join(output, "index.html"));
  const types = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript",
    ".css": "text/css",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
  };
  const server = http.createServer(async (req, res) => {
    const pathname = decodeURIComponent(
      new URL(req.url, "http://localhost").pathname,
    );
    const file = path.resolve(
      output,
      pathname.slice(base.length) || "index.html",
    );
    if (!pathname.startsWith(base) || !file.startsWith(output + path.sep)) {
      res.writeHead(404).end();
      return;
    }
    try {
      res.setHeader(
        "Content-Type",
        types[path.extname(file)] || "application/octet-stream",
      );
      res.end(await fs.readFile(file));
    } catch (error) {
      res.writeHead(error.code === "ENOENT" ? 404 : 500).end();
    }
  });
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  let browser;
  try {
    browser = await chromium.launch({
      executablePath: process.env.E2E_BROWSER_PATH,
      headless: true,
    });
    const origin = `http://127.0.0.1:${server.address().port}`;
    for (const [width, height] of [
      [1440, 900],
      [390, 844],
    ]) {
      const context = await browser.newContext({ viewport: { width, height } });
      const errors = [];
      const requests = [];
      await context.route("**/*", (route) => {
        const url = new URL(route.request().url());
        if (url.origin === origin && url.pathname.startsWith(base))
          return route.continue();
        requests.push(url.href);
        return route.abort();
      });
      const page = await context.newPage();
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("response", (response) => {
        if (response.status() >= 400)
          errors.push(`${response.status()} ${response.url()}`);
      });
      // Act（执行）：进入展示页，滚动至底部并使用页内导航，刷新后再次读取。
      await page.goto(origin + base);
      await page.locator("#opening-title").waitFor();
      await page
        .locator(".drrr-film")
        .evaluate((el) => el.scrollTo(0, el.scrollHeight));
      await page
        .locator(".drrr-film img")
        .evaluateAll((imgs) => Promise.all(imgs.map((img) => img.decode())));
      await page.getByRole("link", { name: "回到开端 ↑", exact: true }).click();
      await page.waitForFunction(
        () => document.querySelector(".drrr-film").scrollTop < 10,
      );
      await page.reload();
      await page.locator("#opening-title").waitFor();
      // Assert（断言）：展示版入口有效，资源无缺失，无横向溢出或业务请求。
      assert.equal(
        await page.locator(".film-nav-enter").innerText(),
        "查看项目 ↗",
      );
      for (const selector of [
        ".film-nav-enter",
        ".story-composer",
        ".film-cta",
        ".film-continuations a",
      ]) {
        const hrefs = await page
          .locator(selector)
          .evaluateAll((links) => links.map((link) => link.href));
        assert.ok(hrefs.length > 0);
        assert.ok(
          hrefs.every((href) => href.startsWith(repo)),
          `${selector} 应指向仓库`,
        );
      }
      assert.equal(
        await page
          .locator(".drrr-film")
          .evaluate((el) => el.scrollWidth <= el.clientWidth),
        true,
      );
      assert.deepEqual(requests, []);
      assert.deepEqual(errors, []);
      await page.screenshot({
        path: path.resolve(__dirname, `../.tmp/pages-${width}.png`),
      });
      console.log(`PASS Pages ${width}x${height}: 资源、导航、刷新、业务隔离`);
      await context.close();
    }
    const noJs = await browser.newContext({ javaScriptEnabled: false });
    const page = await noJs.newPage();
    await page.goto(origin + base);
    await page
      .getByRole("heading", { name: "DOLLARS.", exact: true })
      .waitFor();
    assert.equal(
      await page
        .getByRole("link", { name: "查看项目源码" })
        .getAttribute("href"),
      repo,
    );
    await noJs.close();
    console.log("PASS Pages 禁用 JavaScript 时保留介绍和仓库入口");
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve())),
    );
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
