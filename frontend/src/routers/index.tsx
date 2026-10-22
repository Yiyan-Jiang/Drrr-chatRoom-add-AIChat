/** 定义应用路由、页面延迟加载和登录状态守卫。 */
/* eslint-disable react-refresh/only-export-components */
import { lazy } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import App from '../App'
import { useAuth } from '../contexts/AuthContext'
import GateGuard from '@/components/routes/GateGuard'

const Login = lazy(() => import('../pages/auth/Login'))
const Register = lazy(() => import('../pages/auth/Register'))
const Ddddr = lazy(() => import('../pages/auth/Ddddr'))

const MainLayout = lazy(() => import('../pages/subPage/MainLayout'))
const MyPage = lazy(() => import('../pages/subPage/MyPage'))
const FriendsPage = lazy(() => import('../pages/subPage/FriendsPage'))
const FriendManagementPage = lazy(
  () => import('../pages/subPage/FriendManagementPage'),
)
const ProfilePage = lazy(() => import('../pages/subPage/ProfilePage'))
const SettingsPage = lazy(() => import('../pages/subPage/SettingsPage'))
const HelpPage = lazy(() => import('../pages/subPage/HelpPage'))
const RoomList = lazy(() => import('../pages/subPage/RoomList'))
const RoomSelect = lazy(() => import('../pages/subPage/RoomSelect'))
const NewsFeed = lazy(() => import('../pages/subPage/NewsFeed'))
const NewsArticleDetail = lazy(
  () => import('../pages/subPage/NewsArticleDetail'),
)
const MessageBoard = lazy(() => import('../pages/subPage/MessageBoard'))
const MessageBoardIssueDetail = lazy(
  () => import('../pages/subPage/MessageBoardIssueDetail'),
)
const PostsFeed = lazy(() => import('../pages/subPage/PostsFeed'))
const PostCompose = lazy(() => import('../pages/subPage/PostCompose'))
const PostDetail = lazy(() => import('../pages/subPage/PostDetail'))
const ChatRoom = lazy(() => import('../pages/room/ChatRoom'))
const PrivateChat = lazy(() => import('../pages/room/PrivateChat'))
const NotFound = lazy(() => import('../pages/NotFound'))

/**
 * 等待认证校验结束，再显示子页面或跳转登录页。
 * @param props - 需要登录状态的页面内容。
 * @returns 校验期间为空，校验后返回页面或跳转组件。
 */
function RequireAuth({
  children,
}: {
  /** 认证校验通过后显示的受保护页面。 */ children: React.ReactElement
}) {
  const { isAuthenticated, isAuthChecking } = useAuth()
  if (isAuthChecking) return null
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

/** 包含入口验证、登录守卫及延迟加载页面的应用路由。 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Navigate to="/gate" replace />,
      },
      {
        path: 'gate',
        element: <Ddddr />,
      },
      {
        element: <GateGuard />,
        children: [
          {
            path: 'login',
            element: <Login />,
          },
          {
            path: 'register',
            element: <Register />,
          },
          {
            path: 'chat/:roomId',
            element: (
              <RequireAuth>
                <ChatRoom />
              </RequireAuth>
            ),
          },
          {
            path: 'private-chat/:friendId',
            element: (
              <RequireAuth>
                <PrivateChat />
              </RequireAuth>
            ),
          },
          {
            path: 'news/:slug',
            element: (
              <RequireAuth>
                <NewsArticleDetail />
              </RequireAuth>
            ),
          },
          {
            path: 'board/:issueNumber',
            element: (
              <RequireAuth>
                <MessageBoardIssueDetail />
              </RequireAuth>
            ),
          },
          {
            path: 'posts/new',
            element: (
              <RequireAuth>
                <PostCompose />
              </RequireAuth>
            ),
          },
          {
            path: 'posts/:postId',
            element: (
              <RequireAuth>
                <PostDetail />
              </RequireAuth>
            ),
          },
          {
            element: (
              <RequireAuth>
                <MainLayout />
              </RequireAuth>
            ),
            children: [
              {
                path: 'home',
                element: <RoomList />,
                children: [
                  { index: true, element: <Navigate to="rooms" replace /> },
                  { path: 'news', element: <NewsFeed /> },
                  { path: 'board', element: <MessageBoard /> },
                  { path: 'posts', element: <PostsFeed /> },
                  { path: 'rooms', element: <RoomSelect /> },
                ],
              },
              { path: 'rooms', element: <Navigate to="/home/rooms" replace /> },
              { path: 'my', element: <MyPage /> },
              { path: 'friends', element: <FriendsPage /> },
              { path: 'friends/manage', element: <FriendManagementPage /> },
              { path: 'profile', element: <ProfilePage /> },
              { path: 'settings', element: <SettingsPage /> },
              { path: 'help', element: <HelpPage /> },
            ],
          },
        ],
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
])
