'use client';

import { useState } from 'react';
import PdfUpload from './PdfUpload';
import PdfList from './PdfList';

export default function PdfManager() {
  const [refreshToken, setRefreshToken] = useState(0);

  const handleUploadSuccess = () => {
    setRefreshToken(prev => prev + 1);
  };

  return (
    <div className="space-y-8">
      <PdfUpload onUploadSuccess={handleUploadSuccess} />
      <PdfList key={refreshToken} />
    </div>
  );
}