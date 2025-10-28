import apiClient from './apiClient';
import { User, NotificationSettings } from '../types';

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

  async getNotificationSettings(): Promise<NotificationSettings> {
    const response = await apiClient.get<NotificationSettings>('/users/notifications/settings');
    return response.data;
  }

  async updateNotificationSettings(settings: {
    email_notifications_enabled?: boolean;
    telegram_notifications_enabled?: boolean;
  }): Promise<{ success: boolean; email_notifications_enabled: boolean; telegram_notifications_enabled: boolean }> {
    const response = await apiClient.put('/users/notifications/settings', settings);
    return response.data;
  }

  async sendTestEmail(): Promise<{ status: string; message: string }> {
    const response = await apiClient.post('/users/notifications/test-email');
    return response.data;
  }

  // ========== EMAIL CHANGE ==========
  async requestEmailChange(newEmail: string): Promise<{ status: string; message: string; new_email: string }> {
    const response = await apiClient.post('/users/email/change-request', null, {
      params: { new_email: newEmail }
    });
    return response.data;
  }

  async confirmEmailChange(newEmail: string, code: string): Promise<{ status: string; message: string; new_email: string }> {
    const response = await apiClient.post('/users/email/change-confirm', null, {
      params: { new_email: newEmail, code: code }
    });
    return response.data;
  }

  // ========== TELEGRAM LINKING ==========
  async linkTelegramAccount(code: string): Promise<{ status: string; message: string; telegram_username: string }> {
    const response = await apiClient.post('/users/telegram/link', null, {
      params: { code: code }
    });
    return response.data;
  }

  async unlinkTelegramAccount(): Promise<{ status: string; message: string }> {
    const response = await apiClient.post('/users/telegram/unlink');
    return response.data;
  }
}

const userService = new UserService();
export { userService };
