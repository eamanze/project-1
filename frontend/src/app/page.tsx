'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/auth/useAuth';
import PdfManager from '@/components/PdfManager';
import Search from '@/components/Search';

export default function DashboardPage() {
  const { logout, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'manager' | 'search'>('manager');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 text-gray-600">
        Checking session...
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gray-100 p-6 relative">
      {/* Logout Button */}
      <div className="absolute top-4 right-4">
        <button
          onClick={() => {
            logout();
            router.push('/login');
          }}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Heading */}
      <div className="text-center mt-10 mb-8">
        <h1 className="text-3xl font-bold">📂 Dashboard</h1>
        <p className="text-gray-600">Welcome to your secure dashboard!</p>
      </div>

      {/* Tab Section */}
      <div className="max-w-4xl mx-auto bg-white p-6 rounded shadow">
        {/* Tab Buttons */}
        <div className="flex justify-center space-x-6 mb-6">
          <button
            onClick={() => setActiveTab('manager')}
            className={`px-4 py-2 rounded-t ${
              activeTab === 'manager'
                  ? 'bg-orange-300 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Uploads
          </button>
          <button
            onClick={() => setActiveTab('search')}
            className={`px-4 py-2 rounded-t ${
              activeTab === 'search'
                  ? 'bg-orange-300 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            AI Assistant
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'manager' && <PdfManager />}
        {activeTab === 'search' && <Search />}
      </div>
    </div>
  );
}