import { apiClient } from './client';
import { AxiosError } from 'axios';
import { logger } from '@/utils/logger';

export const gateApi = {
  // gate 提交密码表单
  verify: async (password: string) => {
    logger.debug('[gate] verify request', { hasPassword: Boolean(password) });
    const params = new URLSearchParams();
    params.append('password', password);
    try {
      const { data } = await apiClient.post('/gate/verify', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        withCredentials: true,
      });
      logger.debug('[gate] verify response received');
      return data;
    } catch (error: unknown) {
      throw error;
    }
  },
  // gate 状态验证
  check: async () => {
    logger.debug('[gate] status request');
    try {
      const { data } = await apiClient.get('/gate/status', {
        withCredentials: true,
      });
      logger.debug('[gate] status response received');
      return data;
    } catch (error: unknown) {
      logger.error('[gate] status error', {
        status: error instanceof AxiosError ? error.response?.status : undefined,
        message: error instanceof Error ? error.message : String(error),
      });
      if (error instanceof AxiosError) {
        logger.debug('[gate] status error details', { status: error.response?.status });
      }
      throw error;
    }
  },
};
