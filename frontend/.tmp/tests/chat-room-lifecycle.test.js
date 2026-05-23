import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const testDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(testDir, '..', '..');
const chatRoomSource = readFileSync(resolve(projectRoot, 'src/pages/room/ChatRoom.tsx'), 'utf8');
test('ChatRoom keeps socket room membership stable across normal re-renders', () => {
    assert.match(chatRoomSource, /const\s*\{\s*containerRef,\s*handleScroll,\s*isNearHead,\s*scrollToHead\s*\}\s*=\s*useChatScroll\(\)/, 'ChatRoom should destructure stable callbacks from useChatScroll instead of depending on its return object.');
    assert.match(chatRoomSource, /useRoomChat\(roomIdNum,\s*user,\s*isNearHead,\s*scrollToHead\)/, 'useRoomChat should receive the stable scroll callbacks directly.');
    assert.doesNotMatch(chatRoomSource, /const\s+chatScroll\s*=\s*useChatScroll\(\)/, 'Keeping the full chatScroll object recreates callback dependencies on every render.');
    assert.doesNotMatch(chatRoomSource, /useCallback\(\(\)\s*=>\s*\{[\s\S]*?chatScroll\.scrollToHead\(\)[\s\S]*?\},\s*\[\s*chatScroll\s*\]\s*\)/, 'Wrapping chatScroll.scrollToHead with [chatScroll] makes useRoomChat clean up and leave the socket room on every render.');
    assert.doesNotMatch(chatRoomSource, /\},\s*\[\s*chat,\s*navigate\s*\]\s*\)/, 'openRoomInfo should not depend on the whole chat object because the hook return object is recreated each render.');
});
