import { Outlet } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Toaster } from 'react-hot-toast'

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
