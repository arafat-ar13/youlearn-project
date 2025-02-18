import React, { useEffect, useRef } from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { highlightPlugin, Trigger } from '@react-pdf-viewer/highlight';
import { searchPlugin } from '@react-pdf-viewer/search';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import '@react-pdf-viewer/highlight/lib/styles/index.css';
import '@react-pdf-viewer/search/lib/styles/index.css';

// Interface for block data
interface TextBlock {
  text: string;
  page: number;
  bbox: number[];
  width: number;
  height: number;
  method: string;
}

interface PDFViewerProps {
  fileUrl: string;
  selectedText: string | null;
  selectedBlock: TextBlock[];
}

const PDFViewer: React.FC<PDFViewerProps> = ({ fileUrl, selectedText, selectedBlock }) => {

  if (selectedBlock[0]) {
    console.log(selectedBlock[0].bbox)
  }

  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  
  // Create a reference to store the search plugin instance
  const searchPluginInstanceRef = useRef<ReturnType<typeof searchPlugin> | null>(null);
  
  // Create search plugin
  const searchPluginInstance = searchPlugin();
  searchPluginInstanceRef.current = searchPluginInstance;

  // Handle highlighting the selected text when it changes
  useEffect(() => {
    const performSearch = () => {
      if (!selectedText || !selectedText.trim() || !selectedBlock || selectedBlock.length === 0) {
        return;
      }
      
      // Check the method - only use search plugin for non-azure methods
      const isAzureMethod = selectedBlock[0].method === "azure";
      
      // Clear previous highlights from search plugin
      if (searchPluginInstanceRef.current) {
        searchPluginInstanceRef.current.clearHighlights();
      }
      
      // If not azure method and text is long enough, use search plugin
      if (!isAzureMethod && selectedText.length > 2 && searchPluginInstanceRef.current) {
        searchPluginInstanceRef.current.highlight({
          keyword: selectedText,
          matchCase: false,
          wholeWords: false,
        });
      }
    };

    // Small delay to ensure PDF is loaded
    const timer = setTimeout(performSearch, 500);
    
    return () => {
      clearTimeout(timer);
      // Clear highlights when component unmounts or selection changes
      if (searchPluginInstanceRef.current) {
        searchPluginInstanceRef.current.clearHighlights();
      }
    };
  }, [selectedText, selectedBlock]);

  // Highlight plugin for block-based highlighting (Azure method or short selections)
  const highlightPluginInstance = highlightPlugin({
    trigger: Trigger.None,
    renderHighlights: (props) => {
      // Only proceed if we have a block
      if (!(selectedBlock && selectedBlock.length > 0)) {
        return <></>;
      }
      
      const block = selectedBlock[0];
      
      // Don't render highlight if we're using search highlighting
      // (non-azure method AND text is long enough)
      if (block.method !== "azure" && selectedText && selectedText.length > 2) {
        return <></>;
      }
      
      const height = block.height;
      const width = block.width;
      const  [x0, y0, x1, y1] = block.bbox;
      const page = block.page;
      
      // Only render highlight if we're on the correct page
      if (props.pageIndex !== page) {
        return <></>;
      }

      return (
        <div
          style={Object.assign(
            {},
            {
              background: 'yellow',
              opacity: 0.4,
            },
            props.getCssProperties(
              {
                pageIndex: props.pageIndex,
                height: ((y1-y0)/height)*100,
                width: ((x1-x0)/width)*100,
                left: x0/width*100,
                top: y0/height*100,
              },
              props.rotation
            )
          )}
        />
      );
    },
  });

  // Convert the original URL to use our proxy
  const proxyUrl = `http://localhost:8000/proxy-pdf/${encodeURIComponent(fileUrl)}`;

  return (
    <div className="h-full">
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.js">
        <div className="h-full">
          <Viewer
            fileUrl={proxyUrl}
            plugins={[
              defaultLayoutPluginInstance,
              highlightPluginInstance,
              searchPluginInstance,
            ]}
            withCredentials={false}
          />
        </div>
      </Worker>
    </div>
  );
};

export default PDFViewer;