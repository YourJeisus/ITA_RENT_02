import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Link,
  Divider,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/authStore';
import TelegramLoginWidget from './TelegramLoginWidget';
import styles from './AuthForm.module.scss';
// import { GoogleLogin } from '@react-oauth/google'; // Temporarily disabled
// import { jwtDecode } from 'jwt-decode'; // Temporarily disabled

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`auth-tabpanel-${index}`}
      aria-labelledby={`auth-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AuthForm: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form state
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerPasswordConfirm, setRegisterPasswordConfirm] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setError(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authService.login(loginEmail, loginPassword);
      login(response.access_token, response.user);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка входа. Проверьте email и пароль.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (registerPassword !== registerPasswordConfirm) {
      setError('Пароли не совпадают');
      return;
    }

    if (registerPassword.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        email: registerEmail,
        password: registerPassword,
        first_name: firstName,
        last_name: lastName,
      });

      // После успешной регистрации автоматически входим
      const loginResponse = await authService.login(
        registerEmail,
        registerPassword
      );
      login(loginResponse.access_token, loginResponse.user);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка регистрации. Попробуйте позже.'
      );
    } finally {
      setLoading(false);
    }
  };

  /* // Temporarily disable Google Login
  const handleGoogleSuccess = async (credentialResponse: any) => {
    console.log('Google login success:', credentialResponse);
    setLoading(true);
    setError(null);
    try {
      // credentialResponse.credential - это и есть JWT токен от Google
      // Его нужно отправить на бэкэнд для верификации и получения нашего токена
      const response = await authService.googleLogin({
        token: credentialResponse.credential,
      });
      login(response.access_token, response.user);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Ошибка входа через Google. Попробуйте позже.'
      );
    } finally {
      setLoading(false);
    }
  };
  */

  const handleTelegramSuccess = (user: any) => {
    console.log('Telegram login successful:', user);
    navigate('/');
  };

  const handleTelegramError = (error: string) => {
    setError(error);
  };

  return (
    <Paper className={styles.authForm} elevation={3}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="auth tabs"
        >
          <Tab label="Вход" />
          <Tab label="Регистрация" />
        </Tabs>
      </Box>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      {/* Социальная авторизация - показываем на обеих вкладках */}
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" textAlign="center" sx={{ mb: 2 }}>
          Быстрый вход через социальные сети:
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          {/* 
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => {
              console.log('Google Login Failed');
              setError('Ошибка входа через Google. Попробуйте снова.');
            }}
            useOneTap
            shape="rectangular"
            width="300px"
          />
          */}
          <TelegramLoginWidget
            onSuccess={handleTelegramSuccess}
            onError={handleTelegramError}
            dataSize="medium"
          />
        </Box>

        <Divider sx={{ my: 2 }}>
          <Typography variant="body2" color="text.secondary">
            или
          </Typography>
        </Divider>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={loginEmail}
            onChange={(e) => setLoginEmail(e.target.value)}
            margin="normal"
            required
            autoComplete="email"
          />
          <TextField
            fullWidth
            label="Пароль"
            type="password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            margin="normal"
            required
            autoComplete="current-password"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Войти'}
          </Button>
          <Box textAlign="center">
            <Link href="#" variant="body2">
              Забыли пароль?
            </Link>
          </Box>
        </form>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <form onSubmit={handleRegister}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Имя"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              margin="normal"
              autoComplete="given-name"
            />
            <TextField
              fullWidth
              label="Фамилия"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              margin="normal"
              autoComplete="family-name"
            />
          </Box>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={registerEmail}
            onChange={(e) => setRegisterEmail(e.target.value)}
            margin="normal"
            required
            autoComplete="email"
          />
          <TextField
            fullWidth
            label="Пароль"
            type="password"
            value={registerPassword}
            onChange={(e) => setRegisterPassword(e.target.value)}
            margin="normal"
            required
            autoComplete="new-password"
            helperText="Минимум 6 символов"
          />
          <TextField
            fullWidth
            label="Подтвердите пароль"
            type="password"
            value={registerPasswordConfirm}
            onChange={(e) => setRegisterPasswordConfirm(e.target.value)}
            margin="normal"
            required
            autoComplete="new-password"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Зарегистрироваться'}
          </Button>
          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary">
              Регистрируясь, вы соглашаетесь с{' '}
              <Link href="#" variant="body2">
                условиями использования
              </Link>
            </Typography>
          </Box>
        </form>
      </TabPanel>

      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Или используйте Telegram бота для быстрой регистрации
        </Typography>
        <Button
          variant="outlined"
          sx={{ mt: 1 }}
          onClick={() => window.open('https://t.me/ITA_RENT_BOT', '_blank')}
        >
          Открыть Telegram Bot
        </Button>
      </Box>
    </Paper>
  );
};

export default AuthForm;
