import { useEffect, useState } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import LoginPage from './pages/LoginPage';
import DashboardLayout from './components/DashboardLayout';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('Token on app load:', token);
    console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
    setIsAuthenticated(!!token);
    setLoading(false);

    // Optional: redirect if token is missing
    if (!token && location.pathname !== '/') {
      navigate('/');
    }
  }, [location, navigate]);

  if (loading) return <div className="text-center mt-20">Loading...</div>;

  return (
    <>
      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/notes" replace /> : <LoginPage />}
        />
        <Route
          path="/notes"
          element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/" replace />}
        />
        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </>
  );
}

export default App;
