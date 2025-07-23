import React from 'react';
import { Link } from 'react-router-dom';
import styles from './CallToAction.module.css';

const CallToAction: React.FC = () => {
  return (
    <section className={styles.cta}>
      <div className={styles.container}>
        <h2 className={styles.title}>Готовы найти квартиру мечты?</h2>
        <p className={styles.subtitle}>
          Хватит обновлять сайты вручную. Настройте фильтры один раз и получайте лучшие варианты в Telegram.
        </p>
        <Link to="/filters" className={styles.button}>
          Начать поиск бесплатно
        </Link>
      </div>
    </section>
  );
};

export default CallToAction; 