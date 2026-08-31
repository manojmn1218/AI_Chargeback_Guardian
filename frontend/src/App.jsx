import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import DisputeDetailPage from './pages/DisputeDetailPage';
import AnalyticsPage from './pages/AnalyticsPage';
import LoginPage from './pages/LoginPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<MainLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/disputes/:id" element={<DisputeDetailPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
