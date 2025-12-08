import client from './client';

// 1. register interface
export const register = async (email, password) => {
  // POST /api/register
  const response = await client.post('/register', { email, password });
  return response.data;
};

// 2. login interface
export const login = async (email, password) => {
  // POST /api/login
  // Because the backend returns the token field in Form Data format,
  // but our backend implementation actually receives JSON and returns JSON, so we can directly pass the object here.
  const response = await client.post('/login', { email, password });
  return response.data; // 返回 { access_token: "...", token_type: "bearer" }
};

// 3. get current user info interface
export const getMe = async () => {
  // GET /api/users/me
  // No need to manually pass Token, interceptor will add it automatically
  const response = await client.get('/users/me');
  return response.data; // returns { id: 1, email: "..." }
};