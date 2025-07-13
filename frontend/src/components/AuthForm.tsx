'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/auth/useAuth';
import ForgotPasswordForm from './ForgotPasswordForm';

export default function AuthForm() {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [showForgot, setShowForgot] = useState(false);
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { login, signup } = useAuth();
  const router = useRouter();

  /*const handleSubmit = async () => {
    try {
      if (mode === 'signup') {
        if (!firstName.trim() || !lastName.trim()) {
          alert('First name and last name are required');
          return;
        }
        if (password !== confirmPassword) {
          alert('Passwords do not match!');
          return;
        }

        // ✅ Perform signup and redirect to confirm page
        await signup(email, password, firstName, lastName);
        router.push(`/confirm-signup?email=${encodeURIComponent(email)}`);
      } else {
        await login(email, password);
        router.push('/');
      }
    } catch (e: any) {
      alert(e.message);
    }
  };*/
  const handleSubmit = async () => {
    try {
      if (mode === 'signup') {
        if (!firstName.trim() || !lastName.trim()) {
          alert('First name and last name are required');
          return;
        }
        if (password !== confirmPassword) {
          alert('Passwords do not match!');
          return;
        }
        // Save user info to localStorage for later use
        localStorage.setItem('signup_email', email);
        localStorage.setItem('signup_firstName', firstName);
        localStorage.setItem('signup_lastName', lastName);
  
        const user = await signup(email, password, firstName, lastName);
  
        // Redirect to confirmation page with email
        router.push(`/confirm-signup?email=${encodeURIComponent(email)}`);
      } else {
        await login(email, password);
        router.push('/');
      }
    } catch (e: any) {
      alert(e.message);
    }
  };
  

  const toggleMode = () => setMode((prev) => (prev === 'login' ? 'signup' : 'login'));

  if (showForgot) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
        <ForgotPasswordForm onClose={() => setShowForgot(false)} />
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="bg-white shadow-md rounded-lg p-8 w-full max-w-sm">
        <h2 className="text-2xl font-bold text-center mb-6 capitalize">{mode}</h2>

        {mode === 'signup' && (
          <>
            <input
              placeholder="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="w-full mb-4 p-3 border border-gray-300 rounded"
              required
            />
            <input
              placeholder="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="w-full mb-4 p-3 border border-gray-300 rounded"
              required
            />
          </>
        )}

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-4 p-3 border border-gray-300 rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-3 border border-gray-300 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {mode === 'signup' && (
          <input
            type="password"
            placeholder="Confirm Password"
            className="w-full mb-4 p-3 border border-gray-300 rounded"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        )}

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 transition mb-4"
        >
          {mode === 'signup' ? 'Create Account' : 'Login'}
        </button>

        {mode === 'login' && (
          <button
            onClick={() => setShowForgot(true)}
            className="text-sm text-blue-500 hover:underline mb-2"
          >
            Forgot password?
          </button>
        )}

        <button
          onClick={toggleMode}
          className="text-sm text-blue-500 hover:underline w-full text-center"
        >
          {mode === 'signup'
            ? 'Already have an account? Login'
            : "Don't have an account? Sign up"}
        </button>
      </div>
    </div>
  );
}
