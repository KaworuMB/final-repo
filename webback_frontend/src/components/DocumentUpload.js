import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { authFetch } from '../utils/authFetch'; // JWT fetch

function DocumentUpload() {
  const { id } = useParams(); // project id
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name || file.name);
    formData.append('project', id); // 👈 обязательно

    const response = await authFetch('/api/documents/', {
      method: 'POST',
      body: formData, // без headers
    });

    if (response.ok) {
      alert("Документ загружен успешно");
      window.location.href = `/projects/${id}`; // Перейти назад
    } else {
      alert("Ошибка загрузки");
    }
  };

  return (
    <div className="upload-form">
      <h1>Загрузить документ</h1>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <input
          type="file"
          onChange={e => setFile(e.target.files[0])}
          required
        />
        <input
          type="text"
          placeholder="Название документа (опционально)"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <button type="submit">Загрузить</button>
      </form>
    </div>
  );
}

export default DocumentUpload;
