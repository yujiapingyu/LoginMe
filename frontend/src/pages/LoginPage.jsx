import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../api/auth';
import { TOKEN_KEY } from '../api/client';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      // 1. Call the login interface
      const data = await login(email, password);
      
      // 2. Core step: Save Token to LocalStorage
      // The backend returns data in the structure { access_token: "...", token_type: "bearer" }
      localStorage.setItem(TOKEN_KEY, data.access_token);
      
      // 3. Redirect to home page (personal center)
      navigate('/'); 
      
    } catch (err) {
      console.error(err);
      setError('Email or password is incorrect');
    }
  };

  return (
    <div style={styles.container}>
      <h2>User Login</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputGroup}>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />
        </div>
        <div style={styles.inputGroup}>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={styles.input}
          />
        </div>
        
        {error && <p style={styles.error}>{error}</p>}
        
        <button type="submit" style={styles.button}>Login</button>
      </form>

      <p>
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
    </div>
  );
}

const styles = {
  container: { maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  inputGroup: { display: 'flex', flexDirection: 'column', textAlign: 'left' },
  input: { padding: '8px', fontSize: '16px', marginTop: '5px' },
  button: { padding: '10px', fontSize: '16px', backgroundColor: '#28a745', color: 'white', border: 'none', cursor: 'pointer' },
  error: { color: 'red', fontSize: '14px' }
};

export default LoginPage;