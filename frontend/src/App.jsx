import React, { useState, useEffect } from "react";
import { Home, Search, Settings, User } from "lucide-react";
import "./App.css";

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Проверяем статус API
    fetch("/health")
      .then((response) => response.json())
      .then((data) => {
        setApiStatus(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Ошибка при проверке API:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <div className="logo">
            <Home size={32} />
            <h1>ITA Rent Bot</h1>
          </div>
          <nav className="nav">
            <a href="#" className="nav-link">
              <Search size={20} />
              Поиск
            </a>
            <a href="#" className="nav-link">
              <User size={20} />
              Профиль
            </a>
            <a href="#" className="nav-link">
              <Settings size={20} />
              Настройки
            </a>
          </nav>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <div className="hero">
            <h2>Поиск недвижимости в Италии</h2>
            <p>
              Telegram бот для автоматического поиска и уведомлений о новых
              объявлениях
            </p>

            {loading ? (
              <div className="status loading">
                <div className="spinner"></div>
                <p>Проверяем статус системы...</p>
              </div>
            ) : apiStatus ? (
              <div className="status success">
                <h3>✅ Система работает</h3>
                <div className="status-details">
                  <p>
                    <strong>Приложение:</strong> {apiStatus.app_name}
                  </p>
                  <p>
                    <strong>Версия:</strong> {apiStatus.version}
                  </p>
                  <p>
                    <strong>Окружение:</strong> {apiStatus.environment}
                  </p>
                  <p>
                    <strong>Статус:</strong> {apiStatus.status}
                  </p>
                </div>
              </div>
            ) : (
              <div className="status error">
                <h3>❌ Ошибка подключения к API</h3>
                <p>Проверьте, что backend сервер запущен на порту 8000</p>
              </div>
            )}

            <div className="coming-soon">
              <h3>🚧 В разработке</h3>
              <p>
                Мы активно работаем над созданием удобного интерфейса для поиска
                недвижимости. Скоро здесь появятся:
              </p>
              <ul className="features-list">
                <li>🔍 Расширенный поиск объявлений</li>
                <li>🔔 Настройка уведомлений</li>
                <li>💳 Управление подпиской</li>
                <li>📊 Статистика и аналитика</li>
                <li>🤖 Интеграция с Telegram ботом</li>
              </ul>
            </div>

            <div className="cta">
              <a
                href="/docs"
                className="btn btn-primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                📚 API Документация
              </a>
              <a
                href="https://t.me/your_bot_username"
                className="btn btn-secondary"
              >
                🤖 Telegram Бот
              </a>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 ITA Rent Bot. Все права защищены.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
