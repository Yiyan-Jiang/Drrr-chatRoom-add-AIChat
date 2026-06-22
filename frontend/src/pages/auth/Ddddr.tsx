import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { gateApi } from '@/api/gate';
import AuthBrand from '@/components/auth/AuthBrand';
import GatePasswordForm from '@/components/auth/GatePasswordForm';

export default function Ddddr() {
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await gateApi.verify(password);
      await new Promise(resolve => setTimeout(resolve, 100));
      navigate('/login');
    } catch {
      toast.error('密码错误');
      setPassword('');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black">
       <div className='mb-10'>
        <AuthBrand logoSizeClassName="h-110 w-110" showBanner={false} />
      </div>
      <GatePasswordForm password={password} onPasswordChange={setPassword} onSubmit={handleSubmit} />
    </div>
  );
}
