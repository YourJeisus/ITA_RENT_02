import React from "react";
import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SearchResultsPage from "./pages/SearchResultsPage";
import AuthPage from "./pages/AuthPage";
import FiltersPage from "./pages/FiltersPage";
import MapPage from "./pages/MapPage";
import PageLayout from "./components/layout/PageLayout/PageLayout";
import ProtectedRoute from "./components/common/ProtectedRoute";
import { useAuthStore } from "./store/authStore";
import "./styles/index.scss"; // Import global styles

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    // Инициализация аутентификации при запуске приложения
    checkAuth();
  }, [checkAuth]);

  return (
    <PageLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchResultsPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/filters"
          element={
            <ProtectedRoute>
              <FiltersPage />
            </ProtectedRoute>
          }
        />
        <Route path="/map" element={<MapPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </PageLayout>
  );
}

export default App;
