import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/login.css';

const RegisterPage = () => {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const navigate = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const response = await fetch('http://localhost:8000/api/auth/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });

    if (response.ok) {
      navigate('/login');
    } else {
      alert('Registration failed');
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-header">Register</h2>
      <form onSubmit={handleSubmit}>
        <input name="username" value={form.username} onChange={handleChange} placeholder="Username" />
        <input name="email" value={form.email} onChange={handleChange} placeholder="Email" />
        <input type="password" name="password" value={form.password} onChange={handleChange} placeholder="Password" />
        <button className="login-form__btn" type="submit">Register</button>
      </form>
      <p className="login-form__text">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
};

export default RegisterPage;
