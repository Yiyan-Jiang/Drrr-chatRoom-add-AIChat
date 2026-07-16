import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'

const testDir = dirname(fileURLToPath(import.meta.url))

function findProjectRoot(start: string) {
  let current = start
  for (let depth = 0; depth < 5; depth += 1) {
    if (existsSync(resolve(current, 'src/types/chat.ts'))) return current
    if (existsSync(resolve(current, 'frontend/src/types/chat.ts'))) return resolve(current, 'frontend')
    current = resolve(current, '..')
  }
  throw new Error('Could not find frontend project root')
}

const projectRoot = findProjectRoot(testDir)
const readSource = (path: string) => readFileSync(resolve(projectRoot, path), 'utf8')

test('chat types only own room and message contracts', () => {
  const chatTypes = readSource('src/types/chat.ts')

  assert.doesNotMatch(chatTypes, /export interface LoginCredentials/)
  assert.doesNotMatch(chatTypes, /export interface LoginResponse/)
  assert.doesNotMatch(chatTypes, /export interface RegisterRequest/)
  assert.doesNotMatch(chatTypes, /export interface User(?:\s|\{)/)
  assert.doesNotMatch(chatTypes, /export type AvatarKey/)
  assert.doesNotMatch(chatTypes, /export interface Friend(?:\s|\{)/)
  assert.doesNotMatch(chatTypes, /export type AICharacter/)
})

test('auth files import auth contracts from the auth type module', () => {
  const authApi = readSource('src/api/auth.ts')
  const loginPage = readSource('src/pages/auth/Login.tsx')
  const registerPage = readSource('src/pages/auth/Register.tsx')
  const loginForm = readSource('src/components/auth/LoginForm/LoginForm.tsx')
  const registerForm = readSource('src/components/auth/RegisterForm/RegisterForm.tsx')

  for (const source of [authApi, loginPage, registerPage, loginForm, registerForm]) {
    assert.doesNotMatch(source, /types\/chat/)
  }

  assert.match(authApi, /types\/auth/)
  assert.match(loginPage, /types\/auth/)
  assert.match(registerPage, /types\/auth/)
})
