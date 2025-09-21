import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

function LoginPage({ setNotes }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const isPasswordValid =
    password.length >= 8 && /\d/.test(password) && /[A-Z]/.test(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isLogin ? '/auth/login' : '/auth/register';

    if (!isLogin && !isPasswordValid) {
      alert(
        'Password must be at least 8 characters, include a number and an uppercase letter'
      );
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('API URL:', API_URL);
      console.log(`Submitting to ${endpoint} with email: ${email}`);

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      console.log('Response:', data);

      if (res.ok && data.access_token) {
        localStorage.setItem('token', data.access_token);
        setTimeout(() => navigate('/notes'), 500); // small delay to allow welcome note creation
      } else {
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      console.error('API call failed:', err);
      setError('Network error or server is down.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-[#0f172a] text-white">
      <div className="absolute top-0 left-0 p-4">
        <h1 className="text-3xl font-bold text-[#34D399]">scríobh</h1>
      </div>

      <div className="flex flex-col rounded-2xl bg-[#1e293b] p-8 shadow-2xl backdrop-blur-md w-full max-w-md">
        <h2 className="text-3xl font-bold mb-6 text-[#34D399] text-center">
          {isLogin ? 'Login' : 'Register'}
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 rounded-lg bg-[#2d3748] border border-transparent focus:border-blue-500 focus:outline-none placeholder-gray-400 text-white"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-2 rounded-lg bg-[#2d3748] border border-transparent focus:border-blue-500 focus:outline-none placeholder-gray-400 text-white"
          />
          {!isLogin && (
            <div className={`text-xs mt-1 ${isPasswordValid ? 'text-green-500' : 'text-red-500'}`}>
              Password must be at least 8 characters, include a number and an uppercase letter.
            </div>
          )}
          <button
            type="submit"
            disabled={loading || (!isLogin && !isPasswordValid)}
            className="mt-4 w-full py-2 rounded-lg bg-blue-600 text-white font-bold transition hover:bg-blue-700 disabled:bg-gray-500 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>

        {error && <p className="mt-4 text-sm text-red-500 text-center">{error}</p>}

        <button
          onClick={() => {
            setIsLogin(!isLogin);
            setError('');
            setPassword('');
          }}
          className="mt-6 text-sm text-center text-blue-400 hover:text-blue-300 transition"
        >
          {isLogin ? 'Need an account? Register here.' : 'Already have an account? Login here.'}
        </button>
      </div>
    </div>
  );
}

export default LoginPage;