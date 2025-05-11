import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/create-project.css';
import { authFetch } from '../utils/authFetch';

const ProjectCreatePage = () => {
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authFetch('/api/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project_name: projectName }),
      });

      if (response.ok) {
        navigate('/projects', { state: { reload: true } });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error creating project');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Something went wrong. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <div className="dashboard__profile">
          <span className="dashboard__icon">👤</span>
          <span className="dashboard__label">You</span>
        </div>
        <button className="dashboard__logout" onClick={() => navigate('/login')}>Logout</button>
      </div>

      <h1 className="dashboard__title">Create New Project</h1>

      {loading && <p>Loading...</p>}
      {error && <p className="dashboard__error">{error}</p>}

      <form className="project-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="project_name"
          className="project-form__input"
          placeholder="Enter project name"
          required
          value={projectName}
          onChange={e => setProjectName(e.target.value)}
        />
        <button type="submit" className="project-form__button" disabled={loading}>
          {loading ? 'Creating...' : 'Create'}
        </button>
      </form>
    </div>
  );
};

export default ProjectCreatePage;

