import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import ProjectDashboard from './components/ProjectDashboard';
import ProjectCreatePage from './components/ProjectCreatePage';
import ProjectDetailsPage from './components/ProjectDetails';
import ProjectUploadPage from './components/DocumentUpload';
import ProjectMembersPage from './components/ProjectMembers';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children }) => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
      navigate('/login');
    } else {
      setIsAuthenticated(true);
    }
  }, [navigate]);

  if (!isAuthenticated) {
    return null; // или можно вернуть spinner, если нужно
  }

  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={
          localStorage.getItem('access') ? <Navigate to="/projects" /> : <Navigate to="/login" />
        } />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/projects" element={<PrivateRoute><ProjectDashboard /></PrivateRoute>} />
        <Route path="/projects/create" element={<PrivateRoute><ProjectCreatePage /></PrivateRoute>} />
        <Route path="/projects/:id" element={<PrivateRoute><ProjectDetailsPage /></PrivateRoute>} />
        <Route path="/projects/:id/upload" element={<PrivateRoute><ProjectUploadPage /></PrivateRoute>} />
        <Route path="/projects/:id/members" element={<PrivateRoute><ProjectMembersPage /></PrivateRoute>} />
      </Routes>
    </Router>
  );
}

export default App;



