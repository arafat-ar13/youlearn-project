'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { extractPdfText } from '@/services/api';
import ReactMarkdown from 'react-markdown';

// Dynamically import the PDF viewer components with no SSR
const PDFViewer = dynamic(
  () => import('@/components/PDFViewer'),
  { ssr: false }
);

export default function Home() {
  const [inputUrl, setInputUrl] = useState('');
  const [processedUrl, setProcessedUrl] = useState('');
  const [pdfText, setPdfText] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const data = await extractPdfText(inputUrl);
      setPdfText(data.text);
      setProcessedUrl(inputUrl);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Input form */}
        <div className="flex gap-4 p-6 bg-white rounded-lg shadow-sm">
          <input 
            type="url" 
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
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

        {/* Split view container */}
        {processedUrl && (
          <div className="grid grid-cols-2 gap-6 h-screen">
            {/* PDF Viewer */}
            <div className="bg-white rounded-lg shadow-sm p-4 h-full overflow-hidden">
              <h2 className="text-xl font-semibold mb-4 text-black">PDF View</h2>
              <div className="h-full">
                <PDFViewer fileUrl={processedUrl} />
              </div>
            </div>

            {/* Extracted Text */}
            {pdfText && (
              <div className="bg-white rounded-lg shadow-sm p-4 h-full overflow-auto">
                <h2 className="text-xl font-semibold mb-4 text-black">Extracted Text</h2>
                <div className="prose max-w-none text-black px-4">
                  <ReactMarkdown
                    components={{
                      // Style headers
                      h2: ({node, ...props}) => <h2 className="text-xl font-semibold mt-6 mb-4 text-center" {...props} />,
                      // Style paragraphs
                      p: ({node, ...props}) => <p className="mb-4 text-base leading-relaxed" {...props} />,
                      // Style horizontal rules (page breaks)
                      hr: ({node, ...props}) => <hr className="my-8 border-t border-gray-300" {...props} />
                    }}
                  >
                    {pdfText}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}