import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [apiStatus, setApiStatus] = useState<string>("Проверяется...");
  const [backendUrl, setBackendUrl] = useState<string>("http://localhost:8000");

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/health`);
      if (response.ok) {
        const data = await response.json();
        setApiStatus(`✅ API работает (${data.status})`);
      } else {
        setApiStatus(`❌ API недоступен (${response.status})`);
      }
    } catch (error) {
      setApiStatus("❌ Ошибка подключения к API");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏠 ITA Rent Bot</h1>
        <p>Аренда недвижимости в Италии</p>

        <div className="status-section">
          <h2>📊 Статус системы</h2>
          <div className="status-item">
            <strong>Backend API:</strong> {apiStatus}
          </div>
          <div className="status-item">
            <strong>Frontend:</strong> ✅ Работает
          </div>
          <div className="status-item">
            <strong>Деплой:</strong> ✅ Готов к Railway
          </div>
        </div>

        <div className="features-section">
          <h2>🚀 Возможности</h2>
          <ul>
            <li>🔍 Поиск недвижимости по всей Италии</li>
            <li>📱 Уведомления через Telegram</li>
            <li>🗺️ Интерактивные карты</li>
            <li>💾 Сохранение фильтров поиска</li>
            <li>⚡ Быстрый парсинг объявлений</li>
          </ul>
        </div>

        <div className="navigation-section">
          <h2>📋 Навигация</h2>
          <div className="nav-buttons">
            <button onClick={() => window.open("/search", "_blank")}>
              🔍 Поиск объявлений
            </button>
            <button onClick={() => window.open("/map", "_blank")}>
              🗺️ Карта
            </button>
            <button onClick={() => window.open("/auth", "_blank")}>
              🔐 Авторизация
            </button>
            <button onClick={() => window.open("/filters", "_blank")}>
              ⚙️ Фильтры
            </button>
          </div>
        </div>

        <div className="links-section">
          <h2>📚 Документация</h2>
          <div className="doc-links">
            <a
              href={`${backendUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
            >
              📖 API Документация
            </a>
            <a
              href="https://github.com/YourJeisus/ITA_RENT_02"
              target="_blank"
              rel="noopener noreferrer"
            >
              💻 GitHub Repository
            </a>
            <a
              href={`${backendUrl}/health`}
              target="_blank"
              rel="noopener noreferrer"
            >
              🏥 Health Check
            </a>
          </div>
        </div>

        <footer className="app-footer">
          <p>Сделано с ❤️ для поиска жилья в Италии</p>
          <p>
            <small>Версия: 1.0.0 | Статус: Готов к продакшену</small>
          </p>
        </footer>
      </header>
    </div>
  );
}

export default App;
