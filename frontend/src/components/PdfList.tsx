'use client';

import { useEffect, useState } from 'react';

interface PdfFile {
  file_id: string;
  file_name: string;
  s3_uri: string;
  cdn_url: string;
  file_status: string;
  processed_flag: boolean;
  uploaded_by_user: {};
  created_at: string;
}

export default function PdfList() {
  const [pdfs, setPdfs] = useState<PdfFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    fetchPdfs();
  }, []);

  const fetchPdfs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/data/files/`);
      const data = await response.json();
      setPdfs(data);
    } catch (err) {
      console.error('Failed to load PDFs:', err);
    } finally {
      setLoading(false);
    }
  };

  const openDeleteModal = (fileId: string) => {
    setSelectedFileId(fileId);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedFileId) return;
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/data/files/${selectedFileId}/`,
        { method: 'DELETE' }
      );

      if (!response.ok) throw new Error(`Failed to delete file: ${response.status}`);

      setPdfs((prev) => prev.filter((pdf) => pdf.file_id !== selectedFileId));
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete the file.');
    } finally {
      setShowDeleteModal(false);
      setSelectedFileId(null);
    }
  };

  const openPdfModal = (cdnUrl: string) => {
    setPdfUrl(cdnUrl);
    setShowPdfModal(true);
  };

  return (
    <div className="mt-8 w-full max-w-3xl mx-auto bg-white shadow-md rounded-lg p-6">
      <h3 className="text-xl font-semibold mb-4">📚 Uploaded PDFs</h3>

      {loading ? (
        <p className="text-sm text-gray-500">Loading...</p>
      ) : pdfs.length === 0 ? (
        <p className="text-sm text-gray-500">No PDFs uploaded yet.</p>
      ) : (
        <table className="table-auto w-full text-left text-sm">
          <thead>
            <tr className="border-b text-gray-600">
              <th className="pb-2">Filename</th>
              <th className="pb-2">Uploaded At</th>
              <th className="pb-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {pdfs.map((pdf) => (
              <tr key={pdf.file_id} className="border-b hover:bg-gray-50">
                <td className="py-2">{pdf.file_name}</td>
                <td className="py-2">{new Date(pdf.created_at).toLocaleString()}</td>
                <td className="py-2 flex gap-4 items-center">
                  <div className="relative group">
                    <button
                      onClick={() => openPdfModal(pdf.cdn_url)}
                      className="text-blue-600 hover:text-blue-800 text-lg"
                    >
                      🔍
                    </button>
                    <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-700 text-white text-xs px-2 py-1 rounded shadow">
                      View
                    </span>
                  </div>
                  <div className="relative group">
                    <button
                      onClick={() => openDeleteModal(pdf.file_id)}
                      className="text-red-600 hover:text-red-800 text-lg"
                    >
                      🗑️
                    </button>
                    <span className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-700 text-white text-xs px-2 py-1 rounded shadow">
                      Delete
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-[90%] max-w-md">
            <h4 className="text-lg font-semibold mb-4">Confirm Deletion</h4>
            <p className="text-sm text-gray-700 mb-6">
              Are you sure you want to delete this PDF? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-4">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedFileId(null);
                }}
                className="px-4 py-2 rounded bg-gray-300 text-gray-800 hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PDF Viewer Modal */}
      {showPdfModal && pdfUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-[90%] max-w-4xl h-[90%] relative">
            <button
              onClick={() => {
                setShowPdfModal(false);
                setPdfUrl(null);
              }}
              className="absolute top-2 right-2 text-red-600 hover:text-red-800 text-2xl"
            >
              ×
            </button>
            <iframe
              src={pdfUrl}
              title="PDF Preview"
              className="w-full h-full rounded-b-lg"
            />
          </div>
        </div>
      )}
    </div>
  );
}