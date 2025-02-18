import io
from typing import Optional
from google.cloud import vision
from google.cloud.vision_v1 import types
from dotenv import load_dotenv

load_dotenv()

# Initialize Google Cloud Vision client
client = vision.ImageAnnotatorClient()

class GoogleAIPDFExtractor:
    def __init__(self, file_url=None):
        self.file_url = file_url
        self.has_init = False

    def get_text_with_bboxes(self, page_img_bytes, page_num: int, page_width: float, page_height: float) -> dict:
        """
        Extract text and bounding boxes from a PDF page using Google Cloud Vision API.

        Args:
            page_img_bytes: Bytes of the page image
            page_num: Page number (0-based)
            page_width: Width of the page in points
            page_height: Height of the page in points

        Returns:
            Dictionary containing text content and bounding box information
        """
        # Create image content for Vision API
        image = types.Image(content=page_img_bytes)
    
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        blocks = []
        paragraphs = []
        formatted_text = ""
        
        if texts:
            # First element contains all text
            full_text = texts[0].description
            
            # Process paragraph structure more intelligently
            lines = full_text.split('\n')
            current_paragraph = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:  # Empty line indicates a paragraph break
                    if current_paragraph:
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                elif i < len(lines) - 1 and lines[i+1].strip() and (
                    # Check for paragraph breaks based on indentation
                    (line.endswith(('.', '!', '?', ':', '"', "'")) and lines[i+1].strip()[0].isupper()) or
                    # Check for paragraph breaks based on significantly shorter line
                    (len(line) < 0.5 * len(lines[i+1].strip()) and lines[i+1].strip()[0].isupper()) or
                    # Check for bullet points or numbered lists
                    (lines[i+1].strip().startswith(('•', '-', '*')) or 
                     any(lines[i+1].strip().startswith(f"{n}.") for n in range(1, 10)))
                ):
                    current_paragraph.append(line)
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
                else:
                    current_paragraph.append(line)
            
            # Add the last paragraph if any
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
            
            # Create formatted text with proper paragraph spacing
            formatted_text = "\n\n".join(paragraphs)
            
            # From second element onwards, get individual text blocks with bounding boxes
            for text_block in texts[1:]:
                vertices = [(vertex.x, vertex.y) for vertex in text_block.bounding_poly.vertices]
                
                # Extract x and y coordinates from vertices
                x_coords = [vertex[0] for vertex in vertices]
                y_coords = [vertex[1] for vertex in vertices]
                
                # Get min/max coordinates to create bbox in [x0, y0, x1, y1] format
                x0 = min(x_coords)
                y0 = min(y_coords)
                x1 = max(x_coords)
                y1 = max(y_coords)
                
                blocks.append({
                    "text": text_block.description,
                    "page": page_num,
                    "bbox": [x0, y0, x1, y1],
                    "width": page_width,
                    "height": page_height,
                    "method": "google"
                })

        return {
            "text": formatted_text,
            "blocks": blocks
        }