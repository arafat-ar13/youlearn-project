'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { extractPdfText } from '@/services/api';

// Dynamically import the PDF viewer components with no SSR
const PDFViewer = dynamic(
  () => import('@/components/PDFViewer'),
  { ssr: false }
);

// Interface for block data
interface TextBlock {
  text: string;
  page: number;
  bbox: number[];
  width: number;
  height: number;
  method: string;
}

export default function Home() {
  const [inputUrl, setInputUrl] = useState('');
  const [processedUrl, setProcessedUrl] = useState('');
  const [pdfText, setPdfText] = useState<string | null>(null);
  const [textBlocks, setTextBlocks] = useState<TextBlock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [selectedTextBlock, setSelectedTextBlock] = useState<TextBlock[]>([]);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const data = await extractPdfText(inputUrl);
      setPdfText(data.text);
      setTextBlocks(data.blocks);
      console.log("DATA BLOCKSSSS", data.blocks);
      setProcessedUrl(inputUrl);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle text selection in the transcript
  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (!selection || !selection.toString()) return;

    const text = selection.toString().trim();
    if (text) {
      setSelectedText(text);
      // Find the block containing the selected text
      const block = textBlocks.find(block => 
        block.text.includes(text)
      );
      if (block) {
        setSelectedTextBlock([block]);
      }

      // if (block) {
      //   // console.log('Found matching block:', block);
      //   // console.log("Selected text:", text)
      //   // For now, just log the block info
      //   // We'll implement highlighting differently
      // }
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
                <PDFViewer 
                  fileUrl={processedUrl} 
                  selectedText={selectedText}
                  selectedBlock={selectedTextBlock}
                />
              </div>
            </div>

            {/* Extracted Text */}
            {pdfText && (
              <div 
                className="bg-white rounded-lg shadow-sm p-4 h-full overflow-auto"
                onMouseUp={handleTextSelection}
              >
                <h2 className="text-xl font-semibold mb-4 text-black">Extracted Text</h2>
                <div className="prose max-w-none text-black px-4 whitespace-pre-line">
                  {pdfText}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}