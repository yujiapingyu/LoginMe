import axios from 'axios';

// Store access token in memory (safer than localStorage for XSS protection)
let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => {
  return accessToken;
};

export const clearAccessToken = () => {
  accessToken = null;
};

const client = axios.create({
  baseURL: '/api',
  withCredentials: true,  // Important: Allow sending cookies (for refresh token)
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// --- 1. Request Interceptor ---
// Before sending a request
client.interceptors.request.use(
  (config) => {
    // Get access token from memory
    const token = getAccessToken();
    
    // If token exists, add it to Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- 2. Response Interceptor with Refresh Token Logic ---
// Handle 401 errors and automatically refresh access token

let isRefreshing = false;  // Flag: currently refreshing
let failedQueue = [];      // Queue: requests waiting for refresh

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

client.interceptors.response.use(
  (response) => {
    // If status code is 2xx, directly return the response
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // If already refreshing, queue this request
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return client(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;  // Mark as retried
      isRefreshing = true;  // Set refreshing flag
      
      try {
        // Attempt to refresh access token (cookie sent automatically)
        const { data } = await axios.post('/api/refresh', {}, {
          withCredentials: true  // Send refresh token cookie
        });
        
        const newToken = data.access_token;
        setAccessToken(newToken);  // Store in memory
        
        // Process queued requests with new token
        processQueue(null, newToken);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return client(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed - clear token and redirect to login
        processQueue(refreshError, null);
        clearAccessToken();
        
        // Only redirect if not already on login or register page
        const currentPath = window.location.pathname;
        if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
        
      } finally {
        isRefreshing = false;  // Reset refreshing flag
      }
    }
    
    return Promise.reject(error);
  }
);

export default client;