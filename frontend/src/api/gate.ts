import { apiClient } from './client';
import { AxiosError } from 'axios';

export const gateApi = {
  verify: async (password: string) => {
    console.log('[DEBUG] Gate verify request - password:', password);
    const params = new URLSearchParams();
    params.append('password', password);
    try {
      const { data } = await apiClient.post('/gate/verify', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        withCredentials: true,
      });
      console.log('[DEBUG] Gate verify response:', data);
      return data;
    } catch (error: unknown) {
      console.error('[DEBUG] Gate verify error:', error);
      throw error;
    }
  },
  check: async () => {
    console.log('[DEBUG] Gate check request');
    try {
      const { data } = await apiClient.get('/gate/status', {
        withCredentials: true,
      });
      console.log('[DEBUG] Gate check response:', data);
      return data;
    } catch (error: unknown) {
      console.error('[DEBUG] Gate check error:', error);
      if (error instanceof AxiosError) {
        console.error('[DEBUG] Error details:', error.response?.status, error.response?.data);
      }
      throw error;
    }
  },
};
