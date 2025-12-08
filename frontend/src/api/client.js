import axios from 'axios';

export const TOKEN_KEY = 'access_token';

const client = axios.create({
  baseURL: '/api', 
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// --- 1. Request Interceptor ---
// Before sending a request
client.interceptors.request.use(
  (config) => {
    // Get Token from local storage
    const token = localStorage.getItem(TOKEN_KEY);
    
    // if Token exists, add it to Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- 2. Response Interceptor ---
// After receiving a response
client.interceptors.response.use(
  (response) => {
    // If status code is 2xx, directly return the data part
    return response;
  },
  (error) => {
    // If there is an error (e.g., 400, 401, 500)
    if (error.response) {
      // === Core Logic: Handle 401 Unauthorized ===
      if (error.response.status === 401) {
        // 1. Clear invalid Token
        localStorage.removeItem(TOKEN_KEY);
        
        // 2. Force redirect to login page
        // Note: This is not a React component, so we can't use useNavigate. We have to use native redirect.
        // Only redirect if not already on the login page to avoid infinite loop
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default client;