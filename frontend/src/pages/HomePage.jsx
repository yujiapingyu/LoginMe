import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe } from '../api/auth';
import { TOKEN_KEY } from '../api/client';

function HomePage() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // On page load, fetch user information
    const fetchUser = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
      } catch (err) {
        // If an error occurs (e.g., Token expired), the interceptor will automatically handle the redirect,
        // here we can either do nothing or simply log it
        console.error('Failed to fetch user information', err);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = () => {
    // 1. Clear local Token
    localStorage.removeItem(TOKEN_KEY);
    // 2. Redirect to login page
    navigate('/login');
  };

  if (!user) {
    return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading...</div>;
  }

  return (
    <div style={styles.container}>
      <h1>Welcome back!</h1>
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