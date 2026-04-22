export const API_BASE_URL = '{{API_BASE_URL}}' || 'http://localhost:8000/api';

export async function request(path, options = {}) {
  if (!API_BASE_URL) throw new Error('Nenhum backend foi configurado para este laboratório.');
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
