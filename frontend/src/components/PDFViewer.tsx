import React from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { highlightPlugin, Trigger } from '@react-pdf-viewer/highlight';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import '@react-pdf-viewer/highlight/lib/styles/index.css';

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
  selectedBlock: TextBlock[];
}

const PDFViewer: React.FC<PDFViewerProps> = ({ fileUrl, selectedBlock }) => {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  const highlightPluginInstance = highlightPlugin({
    trigger: Trigger.None,
    renderHighlights: (props) => {
      // Only proceed if we have a block
      if (!(selectedBlock && selectedBlock.length > 0)) {
        return <></>;
      }
      
      const block = selectedBlock[0];
      const height = block.height;
      const width = block.width;
      const [x0, y0, x1, y1] = block.bbox;
      const page = block.page;
      
      // Only render highlight if we're on the correct page
      if (props.pageIndex !== page) {
        return <></>;
      }

      // Different highlighting based on method
      if (block.method === "pymupdf") {
        // Regular precise highlighting for pymupdf
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
      } else {
        // For OCR (google), scale the coordinates by DPI ratio (72/300)
        const dpiScale = 72/300;  // PDF coordinates to image coordinates ratio
        
        // Scale the coordinates back to PDF space
        const scaledX0 = x0 * dpiScale;
        const scaledY0 = y0 * dpiScale;
        const scaledX1 = x1 * dpiScale;
        const scaledY1 = y1 * dpiScale;

        console.log("Google coords - Original:", {x0, y0, x1, y1});
        console.log("Google coords - Scaled:", {
          x0: scaledX0, 
          y0: scaledY0, 
          x1: scaledX1, 
          y1: scaledY1
        });

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
                  height: ((scaledY1-scaledY0)/height)*100,
                  width: ((scaledX1-scaledX0)/width)*100,
                  left: (scaledX0/width)*100,
                  top: (scaledY0/height)*100,
                },
                props.rotation
              )
            )}
          />
        );
      }
    },
  });

  // Convert the original URL to use the proxy
  const proxyUrl = `https://backend-blue-leaf-1353.fly.dev/proxy-pdf/${encodeURIComponent(fileUrl)}`;

  return (
    <div className="h-full">
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.js">
        <div className="h-full">
          <Viewer
            fileUrl={proxyUrl}
            plugins={[
              defaultLayoutPluginInstance,
              highlightPluginInstance,
            ]}
            withCredentials={false}
          />
        </div>
      </Worker>
    </div>
  );
};

export default PDFViewer;