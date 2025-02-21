'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { extractPdfText } from '@/services/api';

const PDFViewer = dynamic(
  () => import('@/components/PDFViewer'),
  { ssr: false }
);

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
  const [textBlocks, setTextBlocks] = useState<TextBlock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedBlock, setSelectedBlock] = useState<TextBlock[]>([]);
  const [activeBlockIndex, setActiveBlockIndex] = useState<number | null>(null);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const data = await extractPdfText(inputUrl);
      
      // Sort blocks by page and vertical position
      const sortedBlocks = [...data.blocks].sort((a, b) => {
        if (a.page !== b.page) return a.page - b.page;
        return a.bbox[1] - b.bbox[1];
      });
      
      setTextBlocks(sortedBlocks);
      setProcessedUrl(inputUrl);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBlockClick = (block: TextBlock, index: number) => {
    setSelectedBlock([block]);
    setActiveBlockIndex(index);
  };

  // Function to determine if a block should start a new section
  const shouldStartNewSection = (currentBlock: TextBlock, previousBlock: TextBlock | null): boolean => {
    if (!previousBlock) return true;
    
    // Check if blocks are from different pages
    if (currentBlock.page !== previousBlock.page) return true;
    
    // For Google OCR blocks, check for significant vertical gap
    if (currentBlock.method === 'google') {
      const verticalGap = currentBlock.bbox[1] - previousBlock.bbox[3];
      return verticalGap > 20; // Adjust this threshold as needed
    }
    
    return false;
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
                  selectedBlock={selectedBlock}
                />
              </div>
            </div>

            {/* Extracted Text */}
            {textBlocks.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-4 h-full overflow-auto">
                <h2 className="text-xl font-semibold mb-4 text-black">Extracted Text</h2>
                <div className="prose max-w-none text-black px-4">
                  {textBlocks.map((block, index) => {
                    const startNewSection = shouldStartNewSection(block, textBlocks[index - 1]);
                    
                    return (
                      <div key={index} className={startNewSection ? 'mt-6' : 'mt-0'}>
                        <div
                          onClick={() => handleBlockClick(block, index)}
                          className={`p-2 rounded cursor-pointer transition-all duration-200 ease-in-out
                            ${activeBlockIndex === index ? 'bg-yellow-200' : 'hover:bg-gray-100 hover:border hover:border-gray-300'}
                          `}
                        >
                          {block.text}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}