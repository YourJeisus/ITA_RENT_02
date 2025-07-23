import apiClient from './apiClient';
import { User } from '@/types';

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  telegram_chat_id?: string;
}

interface TelegramLoginData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

interface GoogleLoginData {
  token: string;
}

interface TokenWithUser {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/login', { email, password });

    // После успешного входа получаем данные пользователя
    if (response.data.access_token) {
      apiClient.defaults.headers.common['Authorization'] =
        `Bearer ${response.data.access_token}`;
      const userResponse = await apiClient.post('/auth/test-token');
      return {
        ...response.data,
        user: userResponse.data,
      };
    }

    return response.data;
  }

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.post('/auth/test-token');
    return response.data;
  }

  // Новые методы для социальной авторизации

  async telegramLogin(telegramData: TelegramLoginData): Promise<TokenWithUser> {
    const response = await apiClient.post('/auth/telegram/login', telegramData);

    if (response.data.access_token) {
      this.setAuthToken(response.data.access_token);
    }

    return response.data;
  }

  async linkTelegramAccount(telegramData: TelegramLoginData): Promise<any> {
    const response = await apiClient.post('/auth/link-telegram', telegramData);
    return response.data;
  }

  async googleLogin(googleData: GoogleLoginData): Promise<TokenWithUser> {
    const response = await apiClient.post('/auth/google/login', googleData);

    if (response.data.access_token) {
      this.setAuthToken(response.data.access_token);
    }

    return response.data;
  }

  // Проверка статуса связывания аккаунтов
  async getAccountLinkStatus(): Promise<{
    has_telegram: boolean;
    has_google: boolean;
    telegram_username?: string;
    google_email?: string;
  }> {
    const user = await this.getCurrentUser();
    return {
      has_telegram: !!user.telegram_chat_id,
      has_google: user.email.includes('@gmail.com'), // Упрощенная проверка
      telegram_username: user.telegram_chat_id,
      google_email: user.email.includes('@gmail.com') ? user.email : undefined,
    };
  }

  logout() {
    delete apiClient.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
  }

  setAuthToken(token: string) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('access_token', token);
  }

  getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }
}

export const authService = new AuthService();
