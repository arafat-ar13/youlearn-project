'use client';

import React from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

interface TextBlock {
  text: string;
  page: number;
  bbox: number[];
}

interface PDFViewerProps {
  fileUrl: string;
  selectedBlock: TextBlock | null;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ fileUrl, selectedBlock }) => {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  return (
    <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.js">
      <Viewer
        fileUrl={fileUrl}
        plugins={[defaultLayoutPluginInstance]}
      />
    </Worker>
  );
};

export default PDFViewer;