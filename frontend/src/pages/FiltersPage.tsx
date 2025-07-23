import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Link as LinkIcon,
  DeleteSweep as DeleteSweepIcon,
} from '@mui/icons-material';
import { useAuthStore } from '../store/authStore';
import { filtersService } from '../services/filtersService';
import { userService } from '../services/userService';
import { Filter } from '../types';
import styles from './FiltersPage.module.scss';
import TelegramLinkDialog from '../components/auth/TelegramLinkDialog';

const FiltersPage: React.FC = () => {
  const { user, checkAuth } = useAuthStore();
  const [filter, setFilter] = useState<Partial<Filter>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [isTelegramDialogOpen, setTelegramDialogOpen] = useState(false);

  useEffect(() => {
    const loadFilter = async () => {
      try {
        setLoading(true);
        const data = await filtersService.getUserFilter();
        if (data) {
          setFilter(data);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки фильтра');
      } finally {
        setLoading(false);
      }
    };
    loadFilter();
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = event.target;
    setFilter((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox'
          ? checked
          : type === 'number' && value === ''
            ? null
            : value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const filterToSave = Object.fromEntries(
        Object.entries(filter).filter(([_, v]) => v !== '' && v !== null)
      );
      const updatedFilter =
        await filtersService.createOrUpdateUserFilter(filterToSave);
      setFilter(updatedFilter);
      setSuccess('Фильтр успешно сохранен!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сохранения фильтра');
    } finally {
      setSaving(false);
    }
  };

  const handleUnlinkTelegram = async () => {
    try {
      await userService.unlinkTelegram();
      checkAuth();
    } catch (err: any) {
      setError('Не удалось отвязать аккаунт.');
    }
  };

  const handleResetNotifications = async () => {
    try {
      await filtersService.resetNotifications();
      setSuccess(
        'История уведомлений сброшена. Теперь вы будете получать объявления заново.'
      );
    } catch (err: any) {
      setError('Не удалось сбросить уведомления.');
    }
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container className={styles.filtersPage} maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Настройка вашего фильтра
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Здесь вы можете настроить единственный фильтр для поиска объявлений.
          Уведомления будут приходить в Telegram.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6">Статус уведомлений</Typography>
          <FormControlLabel
            control={
              <Switch
                checked={!!filter.is_active}
                onChange={handleChange}
                name="is_active"
              />
            }
            label={
              filter.is_active ? 'Уведомления активны' : 'Уведомления выключены'
            }
          />
          {user?.telegram_chat_id ? (
            <Alert severity="success" sx={{ mt: 2 }}>
              Ваш аккаунт привязан к Telegram.
              <Button
                size="small"
                color="inherit"
                onClick={handleUnlinkTelegram}
                sx={{ ml: 2 }}
              >
                Отвязать
              </Button>
            </Alert>
          ) : (
            <Alert
              severity="warning"
              action={
                <Button
                  color="inherit"
                  size="small"
                  startIcon={<LinkIcon />}
                  onClick={() => setTelegramDialogOpen(true)}
                >
                  Привязать
                </Button>
              }
              sx={{ mt: 2 }}
            >
              Чтобы получать уведомления, привяжите ваш аккаунт Telegram.
            </Alert>
          )}
        </Box>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Параметры поиска
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="city"
              label="Город (например, Roma)"
              value={filter.city || ''}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="property_type"
              label="Тип жилья (apartment, house...)"
              value={filter.property_type || ''}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="min_price"
              label="Цена от (€)"
              type="number"
              value={filter.min_price || ''}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="max_price"
              label="Цена до (€)"
              type="number"
              value={filter.max_price || ''}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="min_rooms"
              label="Комнат от"
              type="number"
              value={filter.min_rooms || ''}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="max_rooms"
              label="Комнат до"
              type="number"
              value={filter.max_rooms || ''}
              onChange={handleChange}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 3,
          }}
        >
          <Button
            variant="contained"
            color="primary"
            startIcon={
              saving ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <SaveIcon />
              )
            }
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Сохранение...' : 'Сохранить фильтр'}
          </Button>

          <Tooltip title="Сбросить историю уже отправленных вам уведомлений (полезно для теста)">
            <Button
              variant="text"
              color="secondary"
              startIcon={<DeleteSweepIcon />}
              onClick={handleResetNotifications}
            >
              Сбросить уведомления
            </Button>
          </Tooltip>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert
            severity="success"
            sx={{ mt: 3 }}
            onClose={() => setSuccess(null)}
          >
            {success}
          </Alert>
        )}
      </Paper>

      <TelegramLinkDialog
        open={isTelegramDialogOpen}
        onClose={() => setTelegramDialogOpen(false)}
      />
    </Container>
  );
};

export default FiltersPage;
