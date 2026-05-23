import React, { Suspense} from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './routers/index';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Suspense fallback={<div className="flex h-screen items-center justify-center">加载中...</div>}>
      <RouterProvider router={router} />
    </Suspense>
  </React.StrictMode>
);