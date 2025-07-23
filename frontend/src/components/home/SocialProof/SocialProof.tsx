import React from 'react';
import styles from './SocialProof.module.css';

// Плейсхолдеры для логотипов
const logos = [
  { name: 'TechCrunch', logo: 'TC' },
  { name: 'Forbes', logo: 'Forbes' },
  { name: 'Wired', logo: 'WIRED' },
  { name: 'Il Sole 24 Ore', logo: 'Il Sole' },
];

const SocialProof: React.FC = () => {
  return (
    <section className={styles.socialProof}>
      <div className={styles.container}>
        <h2 className={styles.title}>Нам доверяют и о нас говорят</h2>
        <div className={styles.logos}>
          {logos.map((logo) => (
            <div key={logo.name} className={styles.logoPlaceholder}>
              {logo.logo}
            </div>
          ))}
        </div>
        <div className={styles.quoteSection}>
          <blockquote className={styles.quote}>
            «Я устал от бесконечного ручного поиска и решил автоматизировать
            процесс. Так родился этот бот, который помог мне и уже сотням
            других людей найти квартиру мечты в Италии, экономя время и нервы.»
          </blockquote>
          <div className={styles.author}>
            {/* <img src="/path-to-avatar.jpg" alt="Founder" className={styles.avatar} /> */}
            <div className={styles.avatarPlaceholder}></div>
            <div>
              <p className={styles.authorName}>Александр Баранов</p>
              <p className={styles.authorTitle}>Основатель проекта</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProof; 