const BASE_URL = 'http://127.0.0.1:8000';

export const authFetch = async (url, options = {}) => {
  const access = localStorage.getItem('access');
  const refresh = localStorage.getItem('refresh');

  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    Authorization: `Bearer ${access}`,
    ...options.headers,
  };

  const fullUrl = url.startsWith('http') ? url : BASE_URL + url;

  let response = await fetch(fullUrl, {
    ...options,
    headers,
  });

  // Обновление access токена по refresh при 401
  if (response.status === 401 && refresh) {
    const refreshResponse = await fetch(BASE_URL + '/api/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      localStorage.setItem('access', data.access);

      const retryHeaders = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        Authorization: `Bearer ${data.access}`,
        ...options.headers,
      };

      response = await fetch(fullUrl, {
        ...options,
        headers: retryHeaders,
      });
    } else {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      window.location.href = '/login';
    }
  }

  return response;
};

