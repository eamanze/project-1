'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { CognitoUser } from 'amazon-cognito-identity-js';
import { userPool } from '@/auth/cognito';

export default function ConfirmSignupPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const email = searchParams.get('email') || '';
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [message, setMessage] = useState('');

  const handleConfirm = () => {
    setLoading(true);
    const user = new CognitoUser({ Username: email, Pool: userPool });

    user.confirmRegistration(code.trim(), true, async (err, result) => {
      if (err) {
        console.error('❌ Cognito confirmation error:', err.message);
        alert('Confirmation failed: ' + err.message);
        setLoading(false);
        return;
      }

      try {
        const firstName = localStorage.getItem('signup_firstName') || '';
        const lastName = localStorage.getItem('signup_lastName') || '';

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/users/register/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            first_name: firstName,
            last_name: lastName,
            sub: '',
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data?.error || 'Django registration failed');
        }

        localStorage.removeItem('signup_firstName');
        localStorage.removeItem('signup_lastName');
        localStorage.removeItem('signup_email');

        router.push('/login');
      } catch (error: any) {
        console.error('❌ Django registration failed:', error.message);
        alert('Django error: ' + error.message);
      } finally {
        setLoading(false);
      }
    });
  };

  const handleResend = () => {
    setResending(true);
    const user = new CognitoUser({ Username: email, Pool: userPool });

    user.resendConfirmationCode((err, result) => {
      if (err) {
        console.error('❌ Resend code error:', err.message);
        setMessage('❌ ' + err.message);
      } else {
        console.log('✅ Code resent:', result);
        setMessage('✅ A new confirmation code has been sent to your email.');
      }
      setResending(false);
    });
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="bg-white shadow-md rounded-lg p-8 w-full max-w-sm text-center">
        <h2 className="text-2xl font-bold mb-6">Confirm Your Email</h2>
        <p className="mb-4 text-sm text-gray-600">
          Enter the 6-digit code sent to <span className="font-semibold">{email}</span>
        </p>
        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={6}
          placeholder="Confirmation Code"
          value={code}
          onChange={(e) => setCode(e.target.value.trim())}
          className="w-full mb-4 p-3 border border-gray-300 rounded"
        />

        <button
          onClick={handleConfirm}
          disabled={loading}
          className={`w-full py-3 rounded text-white transition mb-4 ${
            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? 'Confirming...' : 'Confirm Account'}
        </button>

        <button
          onClick={handleResend}
          disabled={resending}
          className={`text-sm underline ${
            resending ? 'text-gray-400' : 'text-blue-600 hover:text-blue-700'
          }`}
        >
          {resending ? 'Resending...' : 'Resend Code'}
        </button>

        {message && <p className="mt-4 text-sm text-gray-600">{message}</p>}
      </div>
    </div>
  );
}
