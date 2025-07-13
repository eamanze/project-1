'use client';

import { useState, useRef } from 'react';
import sha256 from 'crypto-js/sha256';
import encHex from 'crypto-js/enc-hex';
import CryptoJS from 'crypto-js';

export default function PdfUpload({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  /*const handleFileSelect = (f: File | null) => {
    if (f && f.type === 'application/pdf') {
      setFile(f);
      setMessage('');
    } else {
      setMessage('❌ Please select a valid PDF file.');
    }
  };*/
  const handleFileSelect = (f: File | null) => {
    if (f && f.type === 'application/pdf') {
      // Force a new File object instance
      const blob = new Blob([f], { type: f.type });
      const newFile = new File([blob], f.name, { type: f.type, lastModified: f.lastModified });
      setFile(newFile);
      setMessage('');
    } else {
      setMessage('❌ Please select a valid PDF file.');
    }
  };


  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files?.[0] || null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    handleFileSelect(e.dataTransfer.files?.[0] || null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const computeFileHash = async (f: File) => {
    console.log("Selected File:", f.name, f.size, f.type);
    //const buffer = await f.arrayBuffer();
    //return sha256(buffer).toString(encHex);
    const buffer = await f.arrayBuffer();
    const uint8Array = new Uint8Array(buffer);

    const wordArray = CryptoJS.lib.WordArray.create(
      Array.from(uint8Array).map(b => (b << 24) >>> 24)
    );

    return CryptoJS.SHA256(wordArray).toString(CryptoJS.enc.Hex);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setMessage('');

    try {
      const file_hash = await computeFileHash(file);
      console.log("📎 File Hash:", file_hash);
      setMessage(`🧾 File hash: ${file_hash}`);


      const uploadReq = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/uploads/upload-request/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_hash,
          file_name: file.name,
          file_size: file.size,
          file_type: file.type
        })
      });

      const uploadData = await uploadReq.json();
      if (!uploadReq.ok) throw new Error(uploadData.detail || uploadData.error || 'Upload request failed');

      const presignedUrl = uploadData.upload_url;
      console.log("Uploading to S3:", presignedUrl);

      const s3Res = await fetch(presignedUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type || 'application/pdf'
        }
      });

      if (!s3Res.ok) throw new Error('Upload to S3 failed');

      setMessage('✅ PDF uploaded to S3 successfully!');
      setFile(null);
      fileInputRef.current!.value = "";

      // Notify parent
      onUploadSuccess();

    } catch (err: any) {
      setMessage('❌ Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex justify-center">
      <div className="bg-white p-6 shadow-lg rounded-lg w-full max-w-md text-center">
        <h3 className="text-xl font-semibold mb-4">📄 Upload a PDF File</h3>
        <div
          className={`border-2 border-dashed rounded p-6 transition cursor-pointer ${
            dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          {file ? (
            <p className="text-sm text-gray-700">{file.name}</p>
          ) : (
            <p className="text-sm text-gray-500">
              Drag and drop your PDF here, or <span className="text-blue-500 underline">click to select</span>
            </p>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`mt-6 w-full py-2 rounded text-white transition ${
            uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {uploading ? 'Uploading...' : 'Upload PDF'}
        </button>

        {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
      </div>
    </div>
  );
}