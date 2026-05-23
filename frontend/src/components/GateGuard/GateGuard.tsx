/**
 * @parm 组件用途：检查门禁状态并保护需要门禁的页面内容。
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { gateApi } from '@/api/gate';

export function GateGuard({ children }: { children: React.ReactElement }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkGate = async () => {
      try {
        await gateApi.check();
        setLoading(false);
      } catch {
        navigate('/gate', { replace: true });
      }
    };
    checkGate();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return children;
}
