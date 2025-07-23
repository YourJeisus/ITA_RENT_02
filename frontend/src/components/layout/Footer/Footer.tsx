import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Footer.module.scss'; // Создадим позже

const Footer: React.FC = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.grid}>
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>ITA RENT BOT</h3>
            <p className={styles.tagline}>Квартиры в Италии. Быстро. Удобно. Без посредников.</p>
          </div>
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Навигация</h3>
            <ul className={styles.linkList}>
              <li><Link to="/">Главная</Link></li>
              <li><Link to="/search">Поиск</Link></li>
              <li><Link to="/filters">Мои фильтры</Link></li>
              <li><Link to="/login">Войти</Link></li>
            </ul>
          </div>
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Информация</h3>
            <ul className={styles.linkList}>
              <li><a href="#features">О сервисе</a></li>
              <li><a href="#how-it-works">Как это работает</a></li>
              {/* <li><Link to="/faq">FAQ</Link></li> */}
            </ul>
          </div>
          <div className={styles.column}>
            <h3 className={styles.columnTitle}>Контакты</h3>
            <ul className={styles.linkList}>
              <li><a href="mailto:support@itarentbot.com">support@itarentbot.com</a></li>
              {/* Social media links can go here */}
            </ul>
          </div>
        </div>
        <div className={styles.bottomBar}>
          <p>&copy; {new Date().getFullYear()} ITA RENT BOT. Все права защищены.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 