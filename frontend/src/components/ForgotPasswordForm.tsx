'use client';

import { useState } from 'react';
import { CognitoUser } from 'amazon-cognito-identity-js';
import { userPool } from '@/auth/cognito';

export default function ForgotPasswordForm({ onClose }: { onClose: () => void }) {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [stage, setStage] = useState<'request' | 'confirm'>('request');

  const handleSendCode = () => {
    const user = new CognitoUser({ Username: email, Pool: userPool });
    user.forgotPassword({
      onSuccess: () => setStage('confirm'),
      onFailure: (err) => alert(err.message),
    });
  };

  const handleConfirmReset = () => {
    const user = new CognitoUser({ Username: email, Pool: userPool });
    user.confirmPassword(code, newPassword, {
      onSuccess: () => {
        alert('Password reset successful!');
        onClose(); // return to login
      },
      onFailure: (err) => alert(err.message),
    });
  };

  return (
    <div className="p-6 rounded bg-white shadow-md w-full max-w-sm">
      <h2 className="text-xl font-semibold mb-4 text-center">Reset Password</h2>

      <input
        type="email"
        placeholder="Email"
        className="w-full mb-4 p-3 border rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={stage === 'confirm'}
      />

      {stage === 'confirm' && (
        <>
          <input
            placeholder="Verification Code"
            className="w-full mb-4 p-3 border rounded"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
          <input
            type="password"
            placeholder="New Password"
            className="w-full mb-4 p-3 border rounded"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </>
      )}

      <button
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        onClick={stage === 'request' ? handleSendCode : handleConfirmReset}
      >
        {stage === 'request' ? 'Send Reset Code' : 'Confirm New Password'}
      </button>

      <button className="mt-4 text-blue-500 w-full text-sm" onClick={onClose}>
        Back to Login
      </button>
    </div>
  );
}
