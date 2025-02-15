'use client';
import { useState } from 'react';
import { extractPdfText } from '@/services/api';

export default function Home() {
  const [pdfUrl, setPdfUrl] = useState('');

  const handleSubmit = async () => {
    try {
      const data = await extractPdfText(pdfUrl);
      console.log(data.text);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-4 p-6 bg-white rounded-lg shadow-sm">
          <input 
            type="url" 
            value={pdfUrl}
            onChange={(e) => setPdfUrl(e.target.value)}
            placeholder="Enter PDF URL"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
          />
          <button 
            onClick={handleSubmit}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Get PDF HAHA
          </button>
        </div>
      </div>
    </main>
  );
}