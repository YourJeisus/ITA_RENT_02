import apiClient from './apiClient';
import { User } from '@/types';

interface TelegramCodeResponse {
  code: string;
}

class UserService {
  async generateTelegramCode(): Promise<TelegramCodeResponse> {
    const response = await apiClient.post<TelegramCodeResponse>(
      '/users/generate-telegram-code'
    );
    return response.data;
  }

  async unlinkTelegram(): Promise<User> {
    const response = await apiClient.post<User>('/users/unlink-telegram');
    return response.data;
  }
}

const userService = new UserService();
export { userService };
