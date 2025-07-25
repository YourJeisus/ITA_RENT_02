import React, { useState } from "react";
import { FilterState } from "../../types";
import { filtersService } from "../../services/filtersService";
import { useAuthStore } from "../../store/authStore";

interface SearchStatusProps {
  searchType: "database" | "scraping" | null;
  searchMessage: string | null;
  totalCount: number;
  isLoading: boolean;
  currentFilters: FilterState | null;
}

const SearchStatus: React.FC<SearchStatusProps> = ({
  searchType,
  searchMessage,
  totalCount,
  isLoading,
  currentFilters,
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const { isAuthenticated } = useAuthStore();

  const handleSaveFilter = async () => {
    if (!currentFilters || !isAuthenticated) return;

    setIsSaving(true);
    setSaveMessage(null);

    try {
      // Формируем данные для сохранения фильтра
      const filterData = {
        name: `Фильтр ${currentFilters.city?.name || "Поиск"} - ${new Date().toLocaleDateString()}`,
        city: currentFilters.city?.name || null,
        min_price: currentFilters.priceMin,
        max_price: currentFilters.priceMax,
        min_rooms:
          currentFilters.rooms && currentFilters.rooms.length > 0
            ? Math.min(...currentFilters.rooms)
            : null,
        max_rooms:
          currentFilters.rooms && currentFilters.rooms.length > 0
            ? Math.max(...currentFilters.rooms)
            : null,
        property_type:
          currentFilters.propertyType === "all"
            ? null
            : currentFilters.propertyType,
        min_area: currentFilters.areaMin,
        max_area: currentFilters.areaMax,
      };

      await filtersService.createOrUpdateUserFilter(filterData);
      setSaveMessage(
        "✅ Фильтр сохранен! Теперь вы будете получать уведомления о новых объявлениях."
      );

      // Убираем сообщение через 5 секунд
      setTimeout(() => setSaveMessage(null), 5000);
    } catch (error: any) {
      console.error("Ошибка сохранения фильтра:", error);

      // Используем улучшенное сообщение об ошибке
      const errorMessage =
        error?.userMessage ||
        error?.response?.data?.detail ||
        "Неизвестная ошибка";
      setSaveMessage(`❌ ${errorMessage}`);

      // Убираем сообщение об ошибке через 7 секунд
      setTimeout(() => setSaveMessage(null), 7000);
    } finally {
      setIsSaving(false);
    }
  };

  const canSaveFilter = currentFilters && isAuthenticated && !isLoading;

  if (isLoading) {
    return (
      <div
        style={{
          padding: "12px 16px",
          backgroundColor: "#f0f9ff",
          border: "1px solid #0ea5e9",
          borderRadius: "8px",
          margin: "16px 0",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <div
          style={{
            width: "16px",
            height: "16px",
            border: "2px solid #0ea5e9",
            borderTop: "2px solid transparent",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }}
        />
        <span style={{ color: "#0369a1", fontWeight: "500" }}>
          Поиск объявлений...
        </span>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (!searchType || !searchMessage) {
    return null;
  }

  const isDatabaseSearch = searchType === "database";
  const backgroundColor = isDatabaseSearch ? "#f0fdf4" : "#fef3c7";
  const borderColor = isDatabaseSearch ? "#22c55e" : "#f59e0b";
  const textColor = isDatabaseSearch ? "#15803d" : "#d97706";
  const icon = isDatabaseSearch ? "⚡" : "🔄";

  return (
    <div>
      <div
        style={{
          padding: "12px 16px",
          backgroundColor,
          border: `1px solid ${borderColor}`,
          borderRadius: "8px",
          margin: "16px 0",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "16px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              flex: 1,
            }}
          >
            <span style={{ fontSize: "16px" }}>{icon}</span>
            <span style={{ color: textColor, fontWeight: "500" }}>
              {searchMessage}
            </span>
          </div>

          {canSaveFilter && (
            <button
              onClick={handleSaveFilter}
              disabled={isSaving}
              style={{
                padding: "6px 12px",
                backgroundColor: "#3b82f6",
                color: "white",
                border: "none",
                borderRadius: "6px",
                fontSize: "12px",
                fontWeight: "500",
                cursor: isSaving ? "not-allowed" : "pointer",
                opacity: isSaving ? 0.7 : 1,
                transition: "all 0.2s",
                whiteSpace: "nowrap",
              }}
              onMouseEnter={(e) => {
                if (!isSaving) {
                  e.currentTarget.style.backgroundColor = "#2563eb";
                }
              }}
              onMouseLeave={(e) => {
                if (!isSaving) {
                  e.currentTarget.style.backgroundColor = "#3b82f6";
                }
              }}
            >
              {isSaving ? (
                <>
                  <span style={{ marginRight: "4px" }}>⏳</span>
                  Сохранение...
                </>
              ) : (
                <>
                  <span style={{ marginRight: "4px" }}>💾</span>
                  Сохранить фильтр
                </>
              )}
            </button>
          )}
        </div>

        {isDatabaseSearch && (
          <div
            style={{
              marginTop: "4px",
              fontSize: "12px",
              color: "#059669",
            }}
          >
            Результаты получены мгновенно из базы данных
          </div>
        )}
        {!isDatabaseSearch && (
          <div
            style={{
              marginTop: "4px",
              fontSize: "12px",
              color: "#d97706",
            }}
          >
            Данные получены через парсинг сайтов
          </div>
        )}
      </div>

      {/* Сообщение о результате сохранения */}
      {saveMessage && (
        <div
          style={{
            padding: "8px 12px",
            backgroundColor: saveMessage.includes("✅") ? "#f0fdf4" : "#fef2f2",
            border: `1px solid ${saveMessage.includes("✅") ? "#22c55e" : "#ef4444"}`,
            borderRadius: "6px",
            margin: "8px 0",
            fontSize: "12px",
            color: saveMessage.includes("✅") ? "#15803d" : "#dc2626",
          }}
        >
          {saveMessage}
        </div>
      )}

      {/* Подсказка для неавторизованных пользователей */}
      {!isAuthenticated && currentFilters && !isLoading && (
        <div
          style={{
            padding: "8px 12px",
            backgroundColor: "#fffbeb",
            border: "1px solid #f59e0b",
            borderRadius: "6px",
            margin: "8px 0",
            fontSize: "12px",
            color: "#d97706",
          }}
        >
          💡 <strong>Войдите в аккаунт</strong>, чтобы сохранить этот фильтр и
          получать уведомления о новых объявлениях через Telegram
        </div>
      )}
    </div>
  );
};

export default SearchStatus;
