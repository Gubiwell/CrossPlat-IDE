import axios from 'axios';

// Cliente HTTP: envia o token JWT automaticamente em todas as requisições
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function errorMessage(err, fallback) {
  return err.response?.data?.erro || fallback;
}

export default api;
