/**
 * @parm 组件用途：展示旧版普通聊天消息气泡。
 */
import type { Message } from '@/types/chat';

interface ChatMessageProps {
  message: Message;
  isOwn: boolean;
  username?: string;
}

export default function ChatMessage({ message, isOwn, username }: ChatMessageProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  const displayName = isOwn ? '你' : username || `用户${message.user_id}`;
  const avatarEmoji = '👤';

  if (isOwn) {
    return (
      <div className="flex justify-end">
        <div className="flex gap-2 max-w-[80%]">
          <div className="flex flex-col items-end gap-1">
            <div className="rounded-2xl rounded-br-none bg-blue-600 text-white px-4 py-3">
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className="mt-1 text-right text-xs opacity-70">
                {formatTime(message.created_at)}
              </div>
            </div>
          </div>
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm">
            {avatarEmoji}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="flex gap-2 max-w-[80%]">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm">
          {avatarEmoji}
        </div>
        <div className="flex flex-col gap-1">
          <div className="text-xs font-medium text-gray-400">{displayName}</div>
          <div className="rounded-2xl rounded-bl-none bg-gray-800 text-gray-100 px-4 py-3">
            <div className="whitespace-pre-wrap">{message.content}</div>
            <div className="mt-1 text-xs text-gray-500">
              {formatTime(message.created_at)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
