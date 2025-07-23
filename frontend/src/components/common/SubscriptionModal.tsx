import React, { useState } from 'react';
import './SubscriptionModal.scss';
import apiClient from '../../services/apiClient';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  filters: {
    city?: string;
    min_price?: number;
    max_price?: number;
    min_rooms?: number;
    max_rooms?: number;
    property_type?: string;
    min_area?: number;
    max_area?: number;
  };
}

interface SubscriptionForm {
  email: string;
  first_name: string;
  filter_name: string;
}

const SubscriptionModal: React.FC<SubscriptionModalProps> = ({
  isOpen,
  onClose,
  filters,
}) => {
  const [form, setForm] = useState<SubscriptionForm>({
    email: '',
    first_name: '',
    filter_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'form' | 'success'>('form');
  const [telegramUrl, setTelegramUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await apiClient.post('/notifications/subscribe', {
        email: form.email,
        first_name: form.first_name,
        filter_name: form.filter_name || 'Мой поиск',
        filters: filters,
      });

      const data = response.data;

      if (data.success) {
        setTelegramUrl(data.telegram_url);
        setStep('success');
      } else {
        alert('Ошибка: ' + data.message);
      }
    } catch (error: any) {
      console.error('Ошибка подписки:', error);
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Произошла ошибка при оформлении подписки';
      alert('Ошибка: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleTelegramRedirect = () => {
    window.open(telegramUrl, '_blank');
    onClose();
  };

  const renderFiltersPreview = () => {
    return (
      <div className="filters-preview">
        <h4>🔍 Параметры поиска:</h4>
        <ul>
          {filters.city && <li>🏙 Город: {filters.city}</li>}
          {(filters.min_price || filters.max_price) && (
            <li>
              💰 Цена: {filters.min_price || 0}€ - {filters.max_price || '∞'}€
            </li>
          )}
          {(filters.min_rooms || filters.max_rooms) && (
            <li>
              🚪 Комнат: {filters.min_rooms || 0} - {filters.max_rooms || '∞'}
            </li>
          )}
          {filters.property_type && <li>🏠 Тип: {filters.property_type}</li>}
          {(filters.min_area || filters.max_area) && (
            <li>
              📐 Площадь: {filters.min_area || 0}м² - {filters.max_area || '∞'}
              м²
            </li>
          )}
        </ul>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="subscription-modal-overlay" onClick={onClose}>
      <div className="subscription-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔔 Подписка на уведомления</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        {step === 'form' && (
          <div className="modal-content">
            <p className="modal-description">
              Получайте уведомления о новых объявлениях в Telegram! Мы будем
              присылать вам только подходящие под ваши критерии квартиры.
            </p>

            {renderFiltersPreview()}

            <form onSubmit={handleSubmit} className="subscription-form">
              <div className="form-group">
                <label htmlFor="email">📧 Email адрес *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={form.email}
                  onChange={handleInputChange}
                  required
                  placeholder="your@email.com"
                />
              </div>

              <div className="form-group">
                <label htmlFor="first_name">👤 Имя</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={form.first_name}
                  onChange={handleInputChange}
                  placeholder="Как к вам обращаться?"
                />
              </div>

              <div className="form-group">
                <label htmlFor="filter_name">📋 Название поиска</label>
                <input
                  type="text"
                  id="filter_name"
                  name="filter_name"
                  value={form.filter_name}
                  onChange={handleInputChange}
                  placeholder="Например: Квартира в центре Рима"
                />
              </div>

              <div className="benefits">
                <h4>✨ Что вы получите:</h4>
                <ul>
                  <li>🚀 Первым узнавайте о новых объявлениях</li>
                  <li>🎯 Только подходящие под ваши критерии варианты</li>
                  <li>📱 Удобные уведомления в Telegram</li>
                  <li>🆓 Бесплатно для одного фильтра</li>
                </ul>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? 'Оформляем...' : '🔔 Подписаться'}
                </button>
              </div>
            </form>
          </div>
        )}

        {step === 'success' && (
          <div className="modal-content success-step">
            <div className="success-icon">🎉</div>
            <h3>Почти готово!</h3>
            <p>
              Для завершения подписки перейдите в Telegram и подтвердите
              активацию. Это займет всего несколько секунд.
            </p>

            <div className="telegram-instructions">
              <h4>📱 Что делать дальше:</h4>
              <ol>
                <li>Нажмите кнопку "Перейти в Telegram"</li>
                <li>Нажмите "START" в чате с ботом</li>
                <li>Подтвердите активацию подписки</li>
                <li>Готово! Ждите уведомления о новых квартирах</li>
              </ol>
            </div>

            <div className="form-actions">
              <button onClick={onClose} className="btn-secondary">
                Закрыть
              </button>
              <button onClick={handleTelegramRedirect} className="btn-telegram">
                📱 Перейти в Telegram
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionModal;
