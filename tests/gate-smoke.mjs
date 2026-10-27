/**
 * 通过真实 HTTP 入口验证门禁签名、按客户端失败限流和冷却恢复。
 * 需直连本机 Uvicorn 监听端口，确保两个回环地址不会被 Docker NAT 合并。
 */
import assert from "node:assert/strict";
import { request } from "node:http";
import { setTimeout as delay } from "node:timers/promises";

const apiUrl = process.env.SMOKE_API_URL || "http://127.0.0.1:8000";
const gatePassword = process.env.CHAT_GATE_PASSWORD;

/**
 * 从指定本机地址访问门禁，保留状态、响应头和正文供场景断言。
 * @param route - 门禁接口的相对路径。
 * @param options - 密码、Cookie 和测试客户端本机地址。
 * @returns HTTP 状态、响应头和解析后的 JSON 正文。
 */
async function gateRequest(route, { password, cookie, localAddress } = {}) {
  const body =
    password === undefined
      ? undefined
      : new URLSearchParams({ password }).toString();
  return new Promise((resolve, reject) => {
    const req = request(
      new URL(`/api/gate/${route}`, apiUrl),
      {
        method: body === undefined ? "GET" : "POST",
        localAddress,
        headers: {
          ...(body === undefined
            ? {}
            : {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": Buffer.byteLength(body),
              }),
          ...(cookie ? { Cookie: cookie } : {}),
        },
      },
      (response) => {
        let text = "";
        response.setEncoding("utf8");
        response.on("data", (chunk) => {
          text += chunk;
        });
        response.on("error", reject);
        response.on("end", () => {
          try {
            resolve({
              status: response.statusCode,
              headers: response.headers,
              body: JSON.parse(text),
            });
          } catch (error) {
            reject(error);
          }
        });
      },
    );
    req.setTimeout(10000, () => req.destroy(new Error("门禁请求超时")));
    req.on("error", reject);
    req.end(body);
  });
}

/** 验证共享主题口令与签名 Cookie，再通过失败窗口验证拒绝和恢复。 */
async function smoke() {
  assert.ok(gatePassword, "必须提供 CHAT_GATE_PASSWORD");
  // Given（前置）：取得真实门禁 Cookie，保留一个不参与失败尝试的本机客户端地址。
  const verified = await gateRequest("verify", { password: gatePassword });
  assert.equal(verified.status, 200);
  const cookie = verified.headers["set-cookie"]
    .find((value) => value.startsWith("gate_passed="))
    .split(";")[0];
  assert.equal((await gateRequest("status", { cookie })).status, 200);
  const parts = cookie.split(".");
  parts[2] = `${parts[2][0] === "a" ? "b" : "a"}${parts[2].slice(1)}`;
  assert.equal(
    (await gateRequest("status", { cookie: parts.join(".") })).status,
    401,
  );

  // When（操作）：先失败两次再成功，确认成功会清除该客户端的失败次数。
  for (let attempt = 0; attempt < 2; attempt++) {
    assert.equal(
      (await gateRequest("verify", { password: `${gatePassword}-wrong` }))
        .status,
      401,
    );
  }
  assert.equal(
    (await gateRequest("verify", { password: gatePassword })).status,
    200,
  );
  for (let attempt = 0; attempt < 5; attempt++) {
    assert.equal(
      (await gateRequest("verify", { password: `${gatePassword}-wrong` }))
        .status,
      401,
    );
  }

  // Then（结果）：达到失败上限后拒绝验证，已有 Cookie 与其他客户端保持可用。
  const blocked = await gateRequest("verify", { password: gatePassword });
  assert.equal(blocked.status, 429, "连续五次失败后必须限流");
  assert.match(blocked.body.detail, /频繁/);
  const retryAfter = Number(blocked.headers["retry-after"]);
  assert.ok(Number.isInteger(retryAfter) && retryAfter > 0 && retryAfter <= 60);
  assert.equal(
    (await gateRequest("verify", { password: `${gatePassword}-wrong` })).status,
    429,
  );
  assert.equal((await gateRequest("status", { cookie })).status, 200);
  assert.equal(
    (
      await gateRequest("verify", {
        password: gatePassword,
        localAddress: "127.0.0.2",
      })
    ).status,
    200,
  );
  console.log("PASS 门禁签名、成功清零、失败限流、客户端隔离和已有 Cookie");

  // When（操作）：遵循服务端明确返回的冷却时间，不使用猜测的固定等待。
  await delay(retryAfter * 1000);
  // Then（结果）：窗口到期后可再次通过真实门禁，并取得有效 Cookie。
  assert.equal(
    (await gateRequest("verify", { password: gatePassword })).status,
    200,
  );
  console.log("PASS 门禁失败窗口到期恢复");
}

try {
  await smoke();
} catch (error) {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
}
