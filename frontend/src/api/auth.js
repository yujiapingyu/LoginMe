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
  // Returns access_token in response, refresh_token set in HttpOnly cookie
  const response = await client.post('/login', { email, password });
  return response.data; // { access_token: "...", token_type: "bearer" }
};

// 3. get current user info interface
export const getMe = async () => {
  // GET /api/users/me
  // Access token automatically added by interceptor
  const response = await client.get('/users/me');
  return response.data; // { id: 1, email: "..." }
};

// 4. refresh access token interface
export const refreshToken = async () => {
  // POST /api/refresh
  // Refresh token sent automatically via cookie
  const response = await client.post('/refresh');
  return response.data; // { access_token: "...", token_type: "bearer" }
};

// 5. logout interface
export const logout = async () => {
  // POST /api/logout
  // Clears refresh token cookie and database entry
  const response = await client.post('/logout');
  return response.data; // { message: "Logged out successfully" }
};