/** 同步认证状态与本地存储，校验当前用户并管理 Socket.IO 连接。 */
/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { usersApi } from '@/api/users'
import { socketManager } from '@/services/socket'
import type { LoginResponse } from '../types/auth'
import type { User } from '../types/user'

/** 认证上下文提供的状态和本地会话操作。 */
interface AuthContextType {
  /** 认证状态中保存的用户资料。 */
  user: User | null
  /** 当前访问令牌。 */
  token: string | null
  /**
   * 写入登录状态与本地存储；访问令牌变化时触发当前用户校验。
   * @param data - 登录接口返回的令牌和用户资料。
   */
  login: (data: LoginResponse) => void
  /**
   * 更新当前用户状态并同步本地存储。
   * @param user - 更新后的完整用户资料。
   */
  updateUser: (user: User) => void
  /** 清理用户、令牌和本地存储，并断开 Socket.IO 连接。 */
  logout: () => void
  /** 令牌与用户资料同时存在时为 true。 */
  isAuthenticated: boolean
  /** 当前用户校验是否仍在进行。 */
  isAuthChecking: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * 提供认证状态并同步本地存储；当前用户校验请求失败时清除会话。
 * @param props - 认证容器属性。
 * @returns 包裹子节点的认证上下文。
 */
export function AuthProvider({
  children,
}: {
  /** 接收认证上下文的页面或组件。 */ children: ReactNode
}) {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token'),
  )
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(() =>
    Boolean(localStorage.getItem('access_token')),
  )

  const clearAuth = useCallback(() => {
    setUser(null)
    setToken(null)
    setIsAuthChecking(false)
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    socketManager.disconnect()
  }, [])

  const login = useCallback((data: LoginResponse) => {
    setUser(data.user)
    setToken(data.access_token)
    setIsAuthChecking(true)
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('access_token', data.access_token)
  }, [])

  const updateUser = useCallback((nextUser: User) => {
    setUser(nextUser)
    localStorage.setItem('user', JSON.stringify(nextUser))
  }, [])

  const logout = useCallback(() => {
    clearAuth()
  }, [clearAuth])

  useEffect(() => {
    let cancelled = false

    /**
     * 查询当前用户并连接 Socket.IO；无令牌时断开连接，校验失败时清除会话。
     * @returns 本轮校验结束的 Promise；已取消的调用不再写入认证状态。
     */
    async function validateToken() {
      if (!token) {
        setIsAuthChecking(false)
        socketManager.disconnect()
        return
      }

      setIsAuthChecking(true)
      try {
        const currentUser = await usersApi.getMe()
        if (cancelled) return
        setUser(currentUser)
        localStorage.setItem('user', JSON.stringify(currentUser))
        socketManager.connect(token)
      } catch {
        if (!cancelled) {
          clearAuth()
        }
      } finally {
        if (!cancelled) {
          setIsAuthChecking(false)
        }
      }
    }

    validateToken()

    return () => {
      cancelled = true
    }
  }, [token, clearAuth])

  useEffect(() => {
    const handleUnauthorized = () => {
      clearAuth()
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [clearAuth])

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      updateUser,
      logout,
      isAuthenticated: Boolean(token && user),
      isAuthChecking,
    }),
    [user, token, login, updateUser, logout, isAuthChecking],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * 读取当前认证上下文。
 * @returns 当前用户、令牌、校验状态与会话操作。
 * @throws 在 AuthProvider 之外调用时抛出错误。
 */
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
