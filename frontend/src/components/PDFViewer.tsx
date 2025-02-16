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
  
  // Convert the original URL to use our proxy
  const proxyUrl = `http://localhost:8000/proxy-pdf/${encodeURIComponent(fileUrl)}`;

  return (
    <div className="h-full">
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.js">
        <div style={{ height: '100%' }}>
          <Viewer
            fileUrl={proxyUrl}
            plugins={[defaultLayoutPluginInstance]}
            withCredentials={false}
          />
        </div>
      </Worker>
    </div>
  );
};

export default PDFViewer;