import { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Toaster } from 'react-hot-toast';
import { gateApi } from './api/gate';

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [gateChecked, setGateChecked] = useState(false);

  useEffect(() => {
    const checkGate = async () => {
      // 如果已经在gate页面，跳过检查
      if (location.pathname === '/gate') {
        setGateChecked(true);
        return;
      }
      try {
        await gateApi.check();
        setGateChecked(true);
      } catch {
        navigate('/gate', { replace: true });
      }
    };
    checkGate();
  }, [navigate, location.pathname]);

  if (!gateChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <AuthProvider>
      <div className="min-h-screen bg-black text-white">
        {/* 全局布局可以在这里放 Header、Sidebar 等 */}
        {/* <Header /> */}

        <main className="min-h-screen">
          <Outlet />   {/* 这里会渲染当前路由对应的页面 */}
        </main>

        {/* 全局 Toast 提示 */}
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
  );
}

export default App;
