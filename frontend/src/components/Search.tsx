'use client';

import { useState, useRef, useEffect } from 'react';

interface FileResult {
  file_id: string;
  file_name: string;
  cdn_url: string;
  file_status: string;
  file_hash?: string;
  s3_uri: string;
  created_at: string;
  processed_flag?: boolean;
  uploaded_by_user: {
    id: number;
    username: string;
    email: string;
  };
}

interface Message {
  query: string;
  file: FileResult;
  response: string;
}

export default function Search() {
  const [query, setQuery] = useState('');
  const [threshold, setThreshold] = useState(0.75);
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileResult | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
      const response = await fetch(
        `${baseUrl}/api/search/?query=${encodeURIComponent(query)}&threshold=${threshold}`,
        {
          method: 'GET',
          credentials: 'include'
        }
      );

      const data = await response.json();

      if (response.ok) {
        setErrorMessage('');
        setMessages(prev => [
          ...prev,
          {
            query,
            file: data.file,
            response: data.response
          }
        ]);
        setQuery('');
      } else {
        setErrorMessage(data?.error || 'No match found.');
        setQuery('');
      }
    } catch (err) {
      console.error('Search failed:', err);
      setErrorMessage('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const openViewer = (file: FileResult) => {
    setSelectedFile(file);
    setShowModal(true);
  };

  const closeViewer = () => setShowModal(false);

  return (
    <div className="max-w-2xl mx-auto p-6 bg-[#f7f9fc] min-h-screen flex flex-col">
      <h1 className="text-2xl font-semibold mb-4 text-center text-gray-800">📄 Which file are you looking for?</h1>

      {/* Message thread */}
      <div className="flex-1 max-h-[70vh] overflow-y-auto space-y-4 pb-4 pr-2 scrollbar-thin scrollbar-thumb-gray-300">
        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-2">
            {/* User query bubble (right) */}
            <div className="flex justify-end">
              <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-xl rounded-br-none shadow max-w-[75%]">
                <span className="text-sm">🧑‍💻 You:</span>
                <p className="text-base mt-1">{msg.query}</p>
              </div>
            </div>

            {/* Assistant response bubble (left) */}
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-xl rounded-bl-none shadow max-w-[75%] text-sm">
                <div className="mb-1 font-semibold">🤖 Best Match:</div>
                <button
                  onClick={() => openViewer(msg.file)}
                  className="text-blue-600 underline hover:text-blue-800"
                >
                  📎 {msg.file.file_name}
                </button>
                <div className="text-gray-500 mt-1">
                  Uploaded by {msg.file.uploaded_by_user.email}
                </div>
                <div className="mt-2">
                  <span className="block text-gray-600 font-medium mb-1">Answer:</span>
                  <p className="text-gray-800">{msg.response}</p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {errorMessage && (
          <div className="flex justify-end">
            <div className="bg-red-100 text-red-800 px-4 py-2 rounded-xl rounded-br-none shadow max-w-[75%] text-sm">
              <span className="font-semibold">⚠️ No Match:</span>
              <p className="mt-1">{errorMessage}</p>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input box + Similarity Threshold */}
      <div className="pt-6 flex flex-col sm:flex-row sm:items-center sm:space-x-2 space-y-2 sm:space-y-0">
        <input
          type="text"
          placeholder="Ask about your uploaded files..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 p-3 rounded-full border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <select
          className="p-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm"
          value={Math.round(threshold * 100)}
          onChange={(e) => setThreshold(Number(e.target.value) / 100)}
        >
          {[90, 85, 80, 75, 65].map(val => (
            <option key={val} value={val}>
              ≥ {val}% match
            </option>
          ))}
        </select>
        <button
          onClick={handleSearch}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full shadow-md transition"
        >
          {loading ? '...' : '↑'}
        </button>
      </div>

      {/* PDF modal */}
      {showModal && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl overflow-hidden shadow-2xl w-[90%] max-w-4xl h-[90%] relative">
            <button
              onClick={closeViewer}
              className="absolute top-3 right-4 text-gray-500 hover:text-red-600 text-xl"
            >
              ✕
            </button>
            <iframe
              src={selectedFile.cdn_url}
              title="PDF Viewer"
              className="w-full h-full border-0"
            />
          </div>
        </div>
      )}
    </div>
  );
}
