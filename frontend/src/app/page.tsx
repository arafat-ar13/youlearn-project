'use client';
import { useState } from 'react';
import { extractPdfText } from '@/services/api';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [pdfUrl, setPdfUrl] = useState('');
  const [pdfText, setPdfText] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const data = await extractPdfText(pdfUrl);
      setPdfText(data.text);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {!pdfText ? (
          // Input form
          <div className="flex gap-4 p-6 bg-white rounded-lg shadow-sm">
            <input 
              type="url" 
              value={pdfUrl}
              onChange={(e) => setPdfUrl(e.target.value)}
              placeholder="Enter PDF URL"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
              disabled={isLoading}
            />
            <button 
              onClick={handleSubmit}
              className={`px-6 py-2 bg-blue-600 text-white font-medium rounded-lg transition-colors ${
                isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'
              }`}
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Get PDF'}
            </button>
          </div>
        ) : (
          // Transcript view
          <div className="p-6 bg-white rounded-lg shadow-sm text-black">
            <h2 className="text-xl font-semibold mb-4">Extracted Text</h2>
            <div className="prose max-w-none">
              <ReactMarkdown>{pdfText}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}