import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import AuthForm from '@/components/auth/AuthForm';
import styles from './AuthPage.module.scss';

const AuthPage: React.FC = () => {
  return (
    <Container maxWidth="sm" className={styles.authPage}>
      <Box sx={{ mt: 8, mb: 4 }}>
        <Typography variant="h3" component="h1" align="center" gutterBottom>
          Добро пожаловать
        </Typography>
        <Typography
          variant="body1"
          align="center"
          color="text.secondary"
          paragraph
        >
          Войдите или зарегистрируйтесь, чтобы начать поиск идеального жилья в
          Италии
        </Typography>
      </Box>
      <AuthForm />
    </Container>
  );
};

export default AuthPage;
