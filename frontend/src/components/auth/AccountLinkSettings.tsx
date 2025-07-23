import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  Avatar,
  CircularProgress,
} from '@mui/material';
import {
  Telegram as TelegramIcon,
  Google as GoogleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { authService } from '../../services/authService';
import TelegramLoginWidget from './TelegramLoginWidget';
import './AccountLinkSettings.scss';

interface AccountStatus {
  has_telegram: boolean;
  has_google: boolean;
  telegram_username?: string;
  google_email?: string;
}

const AccountLinkSettings: React.FC = () => {
  const [accountStatus, setAccountStatus] = useState<AccountStatus | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showTelegramWidget, setShowTelegramWidget] = useState(false);

  useEffect(() => {
    loadAccountStatus();
  }, []);

  const loadAccountStatus = async () => {
    try {
      setLoading(true);
      const status = await authService.getAccountLinkStatus();
      setAccountStatus(status);
    } catch (err: any) {
      setError('Ошибка загрузки статуса аккаунтов');
    } finally {
      setLoading(false);
    }
  };

  const handleTelegramLink = () => {
    setShowTelegramWidget(true);
    setError(null);
  };

  const handleTelegramSuccess = async (user: any) => {
    setSuccess('Telegram аккаунт успешно привязан!');
    setShowTelegramWidget(false);
    await loadAccountStatus();
  };

  const handleTelegramError = (error: string) => {
    setError(error);
    setShowTelegramWidget(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="account-link-settings">
      <Typography variant="h6" gutterBottom>
        Связанные аккаунты
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Свяжите ваш аккаунт с социальными сетями для быстрого входа и получения
        уведомлений
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Telegram Account */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: '#0088cc', mr: 2 }}>
                <TelegramIcon />
              </Avatar>
              <Box>
                <Typography variant="h6">Telegram</Typography>
                <Typography variant="body2" color="text.secondary">
                  Получайте уведомления о новых объявлениях
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="center" gap={1}>
              {accountStatus?.has_telegram ? (
                <Chip
                  icon={<CheckCircleIcon />}
                  label={`Привязан (${accountStatus.telegram_username})`}
                  color="success"
                  variant="outlined"
                />
              ) : (
                <Chip
                  icon={<ErrorIcon />}
                  label="Не привязан"
                  color="default"
                  variant="outlined"
                />
              )}

              {!accountStatus?.has_telegram && (
                <Button
                  variant="contained"
                  size="small"
                  onClick={handleTelegramLink}
                  startIcon={<TelegramIcon />}
                >
                  Привязать
                </Button>
              )}
            </Box>
          </Box>

          {showTelegramWidget && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Нажмите кнопку ниже для привязки Telegram аккаунта:
              </Typography>
              <TelegramLoginWidget
                onSuccess={handleTelegramSuccess}
                onError={handleTelegramError}
                dataSize="medium"
              />
              <Button
                variant="text"
                size="small"
                onClick={() => setShowTelegramWidget(false)}
                sx={{ mt: 1 }}
              >
                Отмена
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Google Account */}
      <Card>
        <CardContent>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box display="flex" alignItems="center">
              <Avatar sx={{ bgcolor: '#4285f4', mr: 2 }}>
                <GoogleIcon />
              </Avatar>
              <Box>
                <Typography variant="h6">Google</Typography>
                <Typography variant="body2" color="text.secondary">
                  Вход через Google аккаунт (скоро)
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="center" gap={1}>
              {accountStatus?.has_google ? (
                <Chip
                  icon={<CheckCircleIcon />}
                  label={`Привязан (${accountStatus.google_email})`}
                  color="success"
                  variant="outlined"
                />
              ) : (
                <Chip
                  icon={<ErrorIcon />}
                  label="Не привязан"
                  color="default"
                  variant="outlined"
                />
              )}

              <Button
                variant="outlined"
                size="small"
                disabled
                startIcon={<GoogleIcon />}
              >
                Скоро
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ mt: 3 }}>
        <Typography variant="caption" color="text.secondary">
          💡 Привязав Telegram, вы сможете получать мгновенные уведомления о
          новых объявлениях, соответствующих вашим фильтрам поиска.
        </Typography>
      </Box>
    </Box>
  );
};

export default AccountLinkSettings;
