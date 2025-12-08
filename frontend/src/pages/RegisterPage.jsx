import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { register } from '../api/auth';

function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear old errors

    try {
      // 1. Call the register interface
      await register(email, password);
      
      // 2. success message
      alert('Registration successful! Please log in.');
      
      // 3. Redirect to login page
      navigate('/login');
    } catch (err) {
      // Handle errors (e.g., email already registered)
      // If the backend returns a detail field, display it; otherwise, show a generic error
      const errorMsg = err.response?.data?.detail || 'Registration failed, please try again';
      setError(errorMsg);
    }
  };

  return (
    <div style={styles.container}>
      <h2>New User Registration</h2>
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
        
        <button type="submit" style={styles.button}>Register</button>
      </form>
      
      <p>
        Already have an account? <Link to="/login">Go to Login</Link>
      </p>
    </div>
  );
}

// Simple inline styles
const styles = {
  container: { maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  inputGroup: { display: 'flex', flexDirection: 'column', textAlign: 'left' },
  input: { padding: '8px', fontSize: '16px', marginTop: '5px' },
  button: { padding: '10px', fontSize: '16px', backgroundColor: '#007BFF', color: 'white', border: 'none', cursor: 'pointer' },
  error: { color: 'red', fontSize: '14px' }
};

export default RegisterPage;