import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      console.log('Response:', data);

      if (res.ok && data.access_token) {
        const token = data.access_token;
        const payload = JSON.parse(atob(token.split('.')[1]));
        const isExpired = payload.exp * 1000 < Date.now();

        if (isExpired) {
          alert('Session expired immediately. Please try logging in again.');
          return;
        }

        localStorage.setItem('token', token);
        navigate('/notes');
      } else {
        alert(data.detail || 'Authentication failed');
      }
    } catch (error) {
      console.error('API call failed:', error);
      alert('Network error or server is down.');
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-[#0f172a] text-white">
      {/* Container for the logo */}
      <div className="absolute top-0 left-0 p-4">
        <h1 className="text-3xl font-bold text-[#34D399]">scríobh</h1>
      </div>

      <div className="flex flex-col rounded-2xl bg-[#1e293b] p-8 shadow-2xl backdrop-blur-md">
        <h2 className="text-3xl font-bold mb-6 text-[#34D399]">
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
            disabled={!isLogin && !isPasswordValid}
            className="mt-4 w-full py-2 rounded-lg bg-blue-600 text-white font-bold transition hover:bg-blue-700 disabled:bg-gray-500 disabled:cursor-not-allowed"
          >
            {isLogin ? 'Login' : 'Register'}
          </button>
        </form>
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="mt-4 text-sm text-center text-blue-400 hover:text-blue-300 transition"
        >
          {isLogin ? 'Need an account? Register here.' : 'Already have an account? Login here.'}
        </button>
      </div>
    </div>
  );
}

export default LoginPage;