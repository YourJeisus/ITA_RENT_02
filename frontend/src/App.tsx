import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NewHomePage from "./pages/NewHomePage";
import NewSearchResultsPage from "./pages/NewSearchResultsPage";
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
    <Routes>
      {/* New Home Page without PageLayout (has its own navbar) */}
      <Route path="/" element={<NewHomePage />} />

      {/* Search page with new design without PageLayout (has its own navbar) */}
      <Route path="/search" element={<NewSearchResultsPage />} />
      <Route
        path="/auth"
        element={
          <PageLayout>
            <AuthPage />
          </PageLayout>
        }
      />
      <Route
        path="/filters"
        element={
          <PageLayout>
            <ProtectedRoute>
              <FiltersPage />
            </ProtectedRoute>
          </PageLayout>
        }
      />
      <Route
        path="/map"
        element={
          <PageLayout>
            <MapPage />
          </PageLayout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
