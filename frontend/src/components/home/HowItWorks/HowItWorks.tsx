import React from 'react';
import styles from './HowItWorks.module.css';

const steps = [
  {
    speaker: 'you',
    text: 'Привет! Я ищу квартиру в Риме, двушку, до 1500 €.',
  },
  {
    speaker: 'bot',
    text: 'Окей, я всё понял. Буду круглосуточно следить за idealista, immobiliare и другими сайтами. Как только появится что-то подходящее, сразу пришлю в Telegram.',
  },
  {
    speaker: 'you',
    text: 'О, круто! А как быстро ты присылаешь?',
  },
  {
    speaker: 'bot',
    text: 'В ту же минуту. Реагировать нужно быстро, хорошие варианты уходят за пару часов. Я помогу тебе быть первым.',
  },
];

const HowItWorks: React.FC = () => {
  return (
    <section className={styles.howItWorks}>
      <div className={styles.container}>
        <h2 className={styles.title}>Как это работает?</h2>
        <div className={styles.dialog}>
          {steps.map((step, index) => (
            <div
              key={index}
              className={`${styles.message} ${
                step.speaker === 'you' ? styles.you : styles.bot
              }`}
            >
              <p>{step.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks; 