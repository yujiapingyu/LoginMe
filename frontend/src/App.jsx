import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';

function App() {
  return (
    <Router>
      <Routes>
        {/* 1. Login Page */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* 2. Register Page */}
        <Route path="/register" element={<RegisterPage />} />
        
        {/* 3. Home Page (default path) */}
        <Route path="/" element={<HomePage />} />
        
        {/* 4. Catch all undefined paths and redirect to Home Page */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;