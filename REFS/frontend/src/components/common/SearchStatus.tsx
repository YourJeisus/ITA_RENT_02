import React from 'react';

interface SearchStatusProps {
  searchType: 'database' | 'scraping' | null;
  searchMessage: string | null;
  totalCount: number;
  isLoading: boolean;
}

const SearchStatus: React.FC<SearchStatusProps> = ({
  searchType,
  searchMessage,
  totalCount,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div
        style={{
          padding: '12px 16px',
          backgroundColor: '#f0f9ff',
          border: '1px solid #0ea5e9',
          borderRadius: '8px',
          margin: '16px 0',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <div
          style={{
            width: '16px',
            height: '16px',
            border: '2px solid #0ea5e9',
            borderTop: '2px solid transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <span style={{ color: '#0369a1', fontWeight: '500' }}>
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

  const isDatabaseSearch = searchType === 'database';
  const backgroundColor = isDatabaseSearch ? '#f0fdf4' : '#fef3c7';
  const borderColor = isDatabaseSearch ? '#22c55e' : '#f59e0b';
  const textColor = isDatabaseSearch ? '#15803d' : '#d97706';
  const icon = isDatabaseSearch ? '⚡' : '🔄';

  return (
    <div
      style={{
        padding: '12px 16px',
        backgroundColor,
        border: `1px solid ${borderColor}`,
        borderRadius: '8px',
        margin: '16px 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '16px' }}>{icon}</span>
        <span style={{ color: textColor, fontWeight: '500' }}>
          {searchMessage}
        </span>
      </div>
      {isDatabaseSearch && (
        <div
          style={{
            marginTop: '4px',
            fontSize: '12px',
            color: '#059669',
          }}
        >
          Результаты получены мгновенно из базы данных
        </div>
      )}
      {!isDatabaseSearch && (
        <div
          style={{
            marginTop: '4px',
            fontSize: '12px',
            color: '#d97706',
          }}
        >
          Данные получены через парсинг сайтов
        </div>
      )}
    </div>
  );
};

export default SearchStatus;
