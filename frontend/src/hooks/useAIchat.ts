// hooks/useAIChat.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import type { AICharacter } from '../types/chat';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

interface UseAIChatOptions {
  character?: AICharacter;
  onError?: (error: Error) => void;
}

interface UseAIChatReturn {
  messages: string;
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearHistory: () => Promise<void>;
  abort: () => void;
}

export function useAIChat(options: UseAIChatOptions = {}): UseAIChatReturn {
  const { character = 'sakura', onError } = options;
  
  // 从 useAuth 获取最新状态
  const { token, isAuthenticated } = useAuth();

  const [messages, setMessages] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);
  const messageBufferRef = useRef<string>('');
  const flushTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flushMessages = useCallback(() => {
    if (flushTimerRef.current) return;

    flushTimerRef.current = setTimeout(() => {
      setMessages(messageBufferRef.current);
      flushTimerRef.current = null;
    }, 8);
  }, []);

  // 取消当前生成
  const abort = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;

    if (readerRef.current) {
      readerRef.current.cancel().catch(() => {});
      readerRef.current = null;
    }

    messageBufferRef.current = '';
    if (flushTimerRef.current) {
      clearTimeout(flushTimerRef.current);
      flushTimerRef.current = null;
    }

    setMessages('');
    setIsLoading(false);
  }, []);

  useEffect(() => {
    return abort;
  }, [abort]);

  // 当性格切换时重置状态
  useEffect(() => {
    // 中止当前生成
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    if (readerRef.current) {
      readerRef.current.cancel().catch(() => {});
      readerRef.current = null;
    }
    messageBufferRef.current = '';
    if (flushTimerRef.current) {
      clearTimeout(flushTimerRef.current);
      flushTimerRef.current = null;
    }
    // 直接重置状态（异步避免警告）
    setTimeout(() => {
      setMessages('');
      setError(null);
      setIsLoading(false);
    }, 0);
  }, [character]);

  // ==================== 发送消息 ====================
  const sendMessage = useCallback(async (message: string) => {
    // 认证检查
    if (!token || !isAuthenticated) {
      setError('请先登录后再和我说悄悄话呀 (´•ω•̥`)');
      return;
    }

    // 取消上一次请求
    abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);
    setMessages('');
    messageBufferRef.current = '';

    try {
      const response = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message, character }),
        signal: controller.signal,
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('登录已过期，请重新登录哦～');
        }
        if (response.status === 429) {
          throw new Error('请求太频繁啦！小樱的服务器要冒烟了！');
        }
        throw new Error(`服务器出小差了 (${response.status})，待会儿再试试吧～`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法读取响应流');

      readerRef.current = reader;
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;

          const data = trimmed.slice(5).trim();

          if (data === '[DONE]') {
            flushMessages();
            setIsLoading(false);
            return;
          }

          if (data.startsWith('错误:')) {
            setError(data.slice(3).trim());
            continue;
          }

          messageBufferRef.current += data;
          flushMessages();
        }
      }

      flushMessages();
    } catch (err) {
      if ((err as Error).name === 'AbortError') return;

      const errorMessage = err instanceof Error ? err.message : '未知错误发生啦';
      setError(errorMessage);
      onError?.(err as Error);
    } finally {
      abortControllerRef.current = null;
      readerRef.current = null;
      if (flushTimerRef.current) {
        clearTimeout(flushTimerRef.current);
        flushTimerRef.current = null;
      }
      setIsLoading(false);
    }
  }, [token, isAuthenticated, character, abort, onError, flushMessages]);

  // ==================== 清空历史 ====================
  const clearHistory = useCallback(async () => {
    if (!token || !isAuthenticated) {
      setError('请先登录才能清空历史记录');
      return;
    }

    abort(); // 中止当前生成
    setError(null);

    try {
      const response = await fetch(
        `${API_URL}/api/ai/chat/history?character=${encodeURIComponent(character)}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        throw new Error(`清空失败 (${response.status})`);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : '清空历史失败';
      setError(msg);
    }
  }, [token, isAuthenticated, character, abort]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearHistory,
    abort,
  };
}
