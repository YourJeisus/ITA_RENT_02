import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  TextField,
  Tooltip,
  IconButton,
  CircularProgress,
  Box,
  Link,
} from '@mui/material';
import { ContentCopy as ContentCopyIcon } from '@mui/icons-material';
import { userService } from '../../services/userService';
import { useAuthStore } from '../../store/authStore';

interface TelegramLinkDialogProps {
  open: boolean;
  onClose: () => void;
}

const TelegramLinkDialog: React.FC<TelegramLinkDialogProps> = ({
  open,
  onClose,
}) => {
  const { checkAuth } = useAuthStore();
  const [telegramCode, setTelegramCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setLoading(true);
      setError(null);
      userService
        .generateTelegramCode()
        .then((response) => {
          setTelegramCode(response.code);
        })
        .catch((err) => {
          setError(
            err.response?.data?.detail || 'Не удалось сгенерировать код.'
          );
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      // Сбрасываем состояние при закрытии
      setTelegramCode(null);
      setError(null);
    }
  }, [open]);

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleDialogClose = () => {
    checkAuth(); // Обновляем инфо о пользователе
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
      <DialogTitle>Связать аккаунт Telegram</DialogTitle>
      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Typography color="error" sx={{ p: 2 }}>
            {error}
          </Typography>
        ) : (
          <>
            <Typography gutterBottom>
              Чтобы получать уведомления в Telegram, привяжите ваш аккаунт.
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              1. Нажмите на кнопку ниже, чтобы открыть чат с ботом. Код будет
              вставлен автоматически.
            </Typography>
            <Link
              component="a"
              href={`https://t.me/ITA_RENT_BOT?start=${telegramCode}`}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ textDecoration: 'none', display: 'block', my: 2 }}
            >
              <Button variant="contained" fullWidth>
                Открыть Telegram и отправить код
              </Button>
            </Link>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              2. Если кнопка не сработала, скопируйте этот код и отправьте его
              боту вручную.
            </Typography>
            <TextField
              fullWidth
              value={telegramCode || ''}
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <Tooltip title="Копировать">
                    <IconButton
                      onClick={() => handleCopyToClipboard(telegramCode || '')}
                    >
                      <ContentCopyIcon />
                    </IconButton>
                  </Tooltip>
                ),
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 1, display: 'block' }}
            >
              Код действителен в течение 10 минут.
            </Typography>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleDialogClose}>Закрыть</Button>
      </DialogActions>
    </Dialog>
  );
};

export default TelegramLinkDialog;
