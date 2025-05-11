import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authFetch } from '../utils/authFetch';
import '../styles/projects.css';

const ProjectDashboard = () => {
  const [projects, setProjects] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const accessToken = localStorage.getItem('access');
    if (!accessToken) {
      navigate('/login');
      return;
    }

    const fetchUser = async () => {
      try {
        const response = await authFetch('/api/auth/current_user/');
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        if (!response.ok) {
          throw new Error('Failed to fetch user');
        }
        const data = await response.json();
        setUser(data);
      } catch (err) {
        console.error('Error fetching user:', err);
      }
    };

    const fetchProjects = async () => {
      try {
        const response = await authFetch('/api/projects/');
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }
        const data = await response.json();
        setProjects(data);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('Something went wrong. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
    fetchProjects();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    navigate('/login');
  };

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <div className="dashboard__profile">
          <span className="dashboard__icon">👤</span>
          <span className="dashboard__label">
            {user ? user.username : 'You'}
          </span>
        </div>
        <button className="dashboard__logout" onClick={handleLogout}>Logout</button>
      </div>

      <h1 className="dashboard__title">Your Projects</h1>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p className="dashboard__error">{error}</p>
      ) : projects.length > 0 ? (
        <div className="dashboard__projects">
          {projects.map(project => (
            <Link to={`/projects/${project.id}`} key={project.id} className="project-card">
              {project.project_name}
            </Link>
          ))}
        </div>
      ) : (
        <p>No projects found.</p>
      )}

      <div className="dashboard__add">
        <Link to="/projects/create" className="add-button">+</Link>
      </div>
    </div>
  );
};

export default ProjectDashboard;
