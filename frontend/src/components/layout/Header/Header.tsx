import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Menu, MenuItem, IconButton, Avatar } from '@mui/material';
import { useAuthStore } from '../../../store/authStore';
import styles from './Header.module.scss';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/');
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleFilters = () => {
    handleClose();
    navigate('/filters');
  };

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          RentAggregator
        </Link>
        <nav className={styles.nav}>
          <Link to="/search">Поиск</Link>
          <Link to="/map">Карта</Link>
          {/* Добавьте другие ссылки по мере необходимости */}
        </nav>
        <div className={styles.actions}>
          {isAuthenticated && user ? (
            <>
              <Button
                className={styles.chatButton}
                variant="outlined"
                onClick={() =>
                  window.open('https://t.me/your_bot_username', '_blank')
                }
              >
                Telegram Bot
              </Button>
              <IconButton
                size="large"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleMenu}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32 }}>
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </Avatar>
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={Boolean(anchorEl)}
                onClose={handleClose}
              >
                <MenuItem disabled>{user.email}</MenuItem>
                <MenuItem onClick={handleProfile}>Профиль</MenuItem>
                <MenuItem onClick={handleFilters}>Мои фильтры</MenuItem>
                <MenuItem onClick={handleLogout}>Выйти</MenuItem>
              </Menu>
            </>
          ) : (
            <>
              <Button variant="outlined" onClick={() => navigate('/auth')}>
                Войти
              </Button>
              <Button
                variant="contained"
                onClick={() => navigate('/auth')}
                sx={{ ml: 1 }}
              >
                Регистрация
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
