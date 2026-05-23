import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { authApi } from '@/api/auth';
import { useAuth } from '@/contexts/AuthContext';
import { handleApiError } from '@/utils/errorHandler';
import type { LoginCredentials } from '@/types/chat';
import ShowUser from '@/components/ShowUser';
import AuthBrand from '@/components/auth/AuthBrand';
import LoginForm from '@/components/auth/LoginForm';

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  const [form, setForm] = useState<LoginCredentials>({
    username: searchParams.get('username') || '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  // 当前聚焦的输入框
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleFocus = (fieldName: string) => {
    setFocusedField(fieldName);
  };

  const handleBlur = () => {
    setFocusedField(null);
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 表单前端验证
    if (!form.username.trim()) {
      toast.error('请输入用户名');
      return;
    }
    
    if (!form.password.trim()) {
      toast.error('请输入密码');
      return;
    }
    
    if (form.username.length < 3) {
      toast.error('用户名至少3个字符');
      return;
    }

    setLoading(true);
    try {
      const response = await authApi.login(form);
      login(response);
      toast.success('登录成功');
      navigate('/home', { replace: true });
    } catch (error: unknown) {
      // 使用统一的错误处理
      handleApiError(error, '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center flex-col bg-[#090909] px-4">

      <div className='mb-10'>
        <AuthBrand logoSizeClassName="h-110 w-110" title="Weclome... !" showBanner={false} />
      </div>

      <LoginForm
        form={form}
        loading={loading}
        focusedField={focusedField}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onSubmit={handleSubmit}
      />
        
        <AuthBrand logoSizeClassName="hidden" />

        <div className="text-center text-sm text-gray-400">
          <span>还没有账户？</span>
          <Link
            to="/register"
            className="ml-1 font-medium hover:text-white hover:underline"
          >
            Register Now
          </Link>
        </div>
        
        <div
        className='bottom-0 right-0 absolute text-black'>
          <ShowUser/>
        </div>
    </div>
  );
}
