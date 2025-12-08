import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, logout as logoutApi } from '../api/auth';
import { clearAccessToken, getAccessToken } from '../api/client';

function HomePage() {
  const [user, setUser] = useState(null);
  const [tokenStatus, setTokenStatus] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;  // Track if component is mounted
    
    // Check token status on mount
    const token = getAccessToken();
    setTokenStatus(token ? 'Token exists in memory' : 'No token in memory - will auto-refresh');
    
    // On page load, fetch user information
    const fetchUser = async () => {
      try {
        const userData = await getMe();
        if (isMounted) {  // Only update state if component is still mounted
          setUser(userData);
          // Update token status after successful fetch
          const newToken = getAccessToken();
          setTokenStatus(newToken ? 'Token exists in memory' : 'No token in memory');
        }
      } catch (err) {
        // If error occurs (e.g., token expired), interceptor handles redirect
        console.error('Failed to fetch user information', err);
      }
    };

    fetchUser();
    
    // Cleanup function: mark component as unmounted
    return () => {
      isMounted = false;
    };
  }, []);

  const handleLogout = async () => {
    try {
      // 1. Call logout API to clear refresh token from database and cookie
      await logoutApi();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // 2. Clear access token from memory
      clearAccessToken();
      // 3. Redirect to login page
      navigate('/login');
    }
  };

  if (!user) {
    return (
      <div style={{textAlign: 'center', marginTop: '50px'}}>
        <p>Loading...</p>
        <p style={{color: '#666', fontSize: '14px'}}>{tokenStatus}</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h1>Welcome back!</h1>
      
      <div style={{...styles.card, backgroundColor: '#e3f2fd', marginBottom: '10px'}}>
        <p style={{margin: '5px 0', fontSize: '14px'}}>
          🔐 <strong>Token Status:</strong> {tokenStatus}
        </p>
        <p style={{margin: '5px 0', fontSize: '12px', color: '#666'}}>
          💡 Refresh the page (F5) to see auto-refresh in action!
        </p>
      </div>
      
      <div style={styles.card}>
        <p><strong>User ID:</strong> {user.id}</p>
        <p><strong>Email:</strong> {user.email}</p>
      </div>
      
      <button onClick={handleLogout} style={styles.logoutButton}>
        Logout
      </button>
    </div>
  );
}

const styles = {
  container: { maxWidth: '600px', margin: '50px auto', textAlign: 'center', fontFamily: 'Arial, sans-serif' },
  card: { border: '1px solid #ddd', padding: '20px', borderRadius: '8px', margin: '20px 0', backgroundColor: '#f9f9f9' },
  logoutButton: { padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '16px' }
};

export default HomePage;