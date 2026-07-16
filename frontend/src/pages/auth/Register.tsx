import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { usersApi } from '@/api/users';
import { handleApiError } from '@/utils/errorHandler';
import type { RegisterRequest } from '@/types/auth';
import ShowUser from '@/components/ShowUser';
import AuthBrand from '@/components/auth/AuthBrand';
import RegisterForm from '@/components/auth/RegisterForm';

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState<RegisterRequest>({
    username: '',
    password: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleConfirmChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfirmPassword(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!form.username.trim() || !form.password.trim()) {
      toast.error('请输入用户名和密码');
      return;
    }
    
    if (form.username.length < 3) {
      toast.error('用户名至少3个字符');
      return;
    }
    
    if (form.password.length < 6) {
      toast.error('密码至少6个字符');
      return;
    }
    
    if (form.password !== confirmPassword) {
      toast.error('两次输入的密码不一致');
      return;
    }

    setLoading(true);
    try {
      await usersApi.register(form);
      toast.success('注册成功！请登录');
      // 跳转到登录页，并传递用户名
      navigate(`/login?username=${encodeURIComponent(form.username)}`);
    } catch (error: unknown) {
      // 使用统一的错误处理
      handleApiError(error, '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#090909] px-4 flex-col">

      <div className='mb-8'>
        <AuthBrand logoSizeClassName="h-90 w-90" showBanner={false} />
      </div>


      <div className="text-center mb-10">
        <h2 className="text-2xl font-bold text-white">Create an account</h2>
        <p className="text-sm mt-2 text-gray-400">Register a new account and join the chat room</p>
      </div>

      <RegisterForm
        form={form}
        confirmPassword={confirmPassword}
        loading={loading}
        onChange={handleChange}
        onConfirmChange={handleConfirmChange}
        onSubmit={handleSubmit}
      />

      <AuthBrand logoSizeClassName="hidden" />

      <div className="text-center text-sm text-gray-400">
        <span>已有账户？</span>
        <Link
          to="/login"
          className="ml-1 font-medium hover:text-white hover:underline"
        >
          Log in now
        </Link>
      </div> 

      <div
        className=' absolute bottom-0 right-0  text-black'>
          <ShowUser/>
      </div>


    </div>
  );
}
