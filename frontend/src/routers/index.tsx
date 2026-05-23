/* eslint-disable react-refresh/only-export-components */
import { lazy } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from '../App';
import { useAuth } from '../contexts/AuthContext';

const Login = lazy(() => import('../pages/auth/Login'));
const Register = lazy(() => import('../pages/auth/Register'));
const Ddddr = lazy(() => import('../pages/auth/Ddddr'));

const MainLayout = lazy(() => import('../pages/subPage/MainLayout'));
const MyPage = lazy(() => import('../pages/subPage/MyPage'));
const FriendsPage = lazy(() => import('../pages/subPage/FriendsPage'));
const MailboxPage = lazy(() => import('../pages/subPage/MailboxPage'));
const ProfilePage = lazy(() => import('../pages/subPage/ProfilePage'));
const SettingsPage = lazy(() => import('../pages/subPage/SettingsPage'));
const HelpPage = lazy(() => import('../pages/subPage/HelpPage'));
const RoomList = lazy(() => import('../pages/subPage/RoomList'));
const RoomSelect = lazy(() => import('../pages/subPage/RoomSelect'));
const NewsFeed = lazy(() => import('../pages/subPage/NewsFeed'));
const MessageBoard = lazy(() => import('../pages/subPage/MessageBoard'));
const ChatRoom = lazy(() => import('../pages/room/ChatRoom'));
const AIChat = lazy(() => import('../pages/room/AIChat'));
const NotFound = lazy(() => import('../pages/NotFound'));

// 路由守卫组件：要求登录
function RequireAuth({ children }: { children: React.ReactElement }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

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
        path: 'ai-chat',
        element: (
          <RequireAuth>
            <AIChat />
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
              { path: 'rooms', element: <RoomSelect /> },
            ],
          },
          { path: 'rooms', element: <Navigate to="/home/rooms" replace /> },
          { path: 'my', element: <MyPage /> },
          { path: 'friends', element: <FriendsPage /> },
          { path: 'mailbox', element: <MailboxPage /> },
          { path: 'profile', element: <ProfilePage /> },
          { path: 'settings', element: <SettingsPage /> },
          { path: 'help', element: <HelpPage /> },
        ],
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);