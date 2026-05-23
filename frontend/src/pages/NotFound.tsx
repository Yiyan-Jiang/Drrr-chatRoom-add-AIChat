import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black p-4">
      <div className="text-center">
        <div className="mb-6 text-9xl font-bold text-gray-800">404</div>
        <h1 className="mb-4 text-3xl font-bold text-white">页面未找到</h1>
        <p className="mb-8 max-w-md text-gray-400">
          您访问的页面可能已被移动、删除或暂时不可用。
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/"
            className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
          >
            返回首页
          </Link>
          <Link
            to="/home/rooms"
            className="rounded-lg border border-gray-700 bg-gray-800 px-6 py-3 font-medium text-white hover:bg-gray-700"
          >
            查看房间列表
          </Link>
          <Link
            to="/login"
            className="rounded-lg border border-gray-700 bg-gray-800 px-6 py-3 font-medium text-white hover:bg-gray-700"
          >
            重新登录
          </Link>
        </div>
        <div className="mt-12 text-sm text-gray-500">
          <p>如果您认为这是一个错误，请检查URL是否正确。</p>
        </div>
      </div>
    </div>
  );
}
