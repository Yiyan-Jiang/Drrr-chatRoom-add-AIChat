import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const testDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(testDir, '..', '..');
const aiChatSource = readFileSync(resolve(projectRoot, 'src/pages/room/AIChat.tsx'), 'utf8');
test('AI chat page reuses normal chat room UI components', () => {
    assert.match(aiChatSource, /from '@\/components\/chat\/ChatRoomHeader'/);
    assert.match(aiChatSource, /from '@\/components\/chat\/ChatMessageViewport'/);
    assert.doesNotMatch(aiChatSource, /AIChatMessage/);
    assert.doesNotMatch(aiChatSource, /AILoadingIndicator/);
    assert.doesNotMatch(aiChatSource, /AIChatEmptyState/);
    assert.doesNotMatch(aiChatSource, /ChatMessageInput/);
    assert.doesNotMatch(aiChatSource, /from '@\/components\/chat\/ChatHeader'/);
    assert.equal(existsSync(resolve(projectRoot, 'src/components/AIchat/AIChatMessage')), false);
    assert.equal(existsSync(resolve(projectRoot, 'src/components/AIchat/AIChatEmptyState')), false);
});
test('AI chat exit returns to room list without logging out', () => {
    assert.doesNotMatch(aiChatSource, /\blogout\(\)/);
    assert.doesNotMatch(aiChatSource, /navigate\('\/login'\)/);
    assert.match(aiChatSource, /navigate\('\/home\/rooms'\)/);
});
test('AI chat page derives character and avatar state from URL and auth user', () => {
    assert.match(aiChatSource, /useSearchParams/);
    assert.match(aiChatSource, /useAuth\(\)/);
    assert.doesNotMatch(aiChatSource, /useState<AICharacter>\('sakura'\)/);
    assert.doesNotMatch(aiChatSource, /AICharacterTabs/);
});
test('AI chat prepends new messages to match the normal chat viewport order', () => {
    assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'user', content: userMessage \},\s*\n\s*\.\.\.prev/);
    assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'system', content: error \},\s*\n\s*\.\.\.prev/);
    assert.match(aiChatSource, /\{ id: Date\.now\(\), role: 'assistant', content: messages \},\s*\n\s*\.\.\.prev/);
    assert.match(aiChatSource, /const head = prev\[0\]/);
});
