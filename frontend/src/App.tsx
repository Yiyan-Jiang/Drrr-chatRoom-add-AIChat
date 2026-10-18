/** 组装认证上下文、页面路由出口和全局消息提示。 */
import { Outlet } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from 'react-hot-toast'

/**
 * 渲染应用级认证容器、路由出口和 toast 提示。
 * @returns 应用根组件。
 */
function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-black text-white">
        <main className="min-h-screen">
          <Outlet />
        </main>

        <Toaster
          position="top-center"
          toastOptions={{
            duration: 3000,
            success: { duration: 2000 },
            error: { duration: 4000 },
          }}
        />
      </div>
    </AuthProvider>
  )
}

export default App
