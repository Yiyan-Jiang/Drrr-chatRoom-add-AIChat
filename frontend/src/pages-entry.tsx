/** 挂载公开项目展示页，不加载认证上下文或业务路由。 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import SettingsPage from './pages/subPage/SettingsPage'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <SettingsPage showcase />
    </BrowserRouter>
  </StrictMode>,
)
