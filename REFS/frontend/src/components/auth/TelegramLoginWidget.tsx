import React, { useEffect, useRef, memo } from 'react';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/authService';
import './TelegramLoginWidget.scss';

interface TelegramLoginWidgetProps {
  onSuccess?: (user: any) => void;
  onError?: (error: string) => void;
  dataSize?: 'small' | 'medium' | 'large';
  dataRequestAccess?: 'write';
  className?: string;
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

declare global {
  interface Window {
    onTelegramAuth: (user: TelegramLoginData) => void;
  }
}

const TelegramLoginWidget: React.FC<TelegramLoginWidgetProps> = ({
  onSuccess,
  onError,
  dataSize = 'large',
  dataRequestAccess = 'write',
  className = '',
}) => {
  const { login } = useAuthStore();
  const containerRef = useRef<HTMLDivElement>(null);

  const handleTelegramAuth = async (telegramData: TelegramLoginData) => {
    try {
      console.log('Telegram auth data received:', telegramData);
      const response = await authService.telegramLogin(telegramData);
      login(response.access_token, response.user);
      onSuccess?.(response.user);
    } catch (error: any) {
      console.error('Telegram login error:', error);
      const errorMessage =
        error.response?.data?.detail || 'Ошибка авторизации через Telegram';
      onError?.(errorMessage);
    }
  };

  useEffect(() => {
    // Make the auth handler function global
    window.onTelegramAuth = handleTelegramAuth;

    if (containerRef.current) {
      const script = document.createElement('script');
      script.src = 'https://telegram.org/js/telegram-widget.js?22';
      script.async = true;
      script.setAttribute(
        'data-telegram-login',
        import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'ita_rent_bot'
      );
      script.setAttribute('data-size', dataSize);
      script.setAttribute('data-onauth', 'onTelegramAuth(user)');
      script.setAttribute('data-request-access', dataRequestAccess);

      // Clear previous widget before appending new one
      containerRef.current.innerHTML = '';
      containerRef.current.appendChild(script);
    }

    return () => {
      // Clean up the global function when the component unmounts
      if (window.onTelegramAuth) {
        delete (window as any).onTelegramAuth;
      }
    };
    // Disabled dependency array to prevent re-rendering and script re-injection
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={`telegram-login-widget ${className}`}>
      <div ref={containerRef} className="telegram-widget-container" />
      <p className="telegram-login-description">
        🔐 Войдите через Telegram для быстрого доступа к уведомлениям
      </p>
    </div>
  );
};

export default memo(TelegramLoginWidget);
