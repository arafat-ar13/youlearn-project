import io
from typing import Optional
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv
import os

load_dotenv()

client_options = ClientOptions(api_key=os.getenv("GOOGLE_API_KEY"))
client = vision.ImageAnnotatorClient(client_options=client_options)

class GoogleAIPDFExtractor:
    def __init__(self, file_url=None):
        self.file_url = file_url
        self.has_init = False

    def should_continue_paragraph(self, prev_line, curr_line):
        """
        Determine if the current line should continue the previous paragraph
        """
        if not prev_line or not curr_line:
            return False
            
        # Get last word of previous line and first word of current line
        prev_text = ' '.join(block['text'] for block in prev_line)
        curr_text = ' '.join(block['text'] for block in curr_line)
        
        # Calculate the vertical gap between lines
        prev_bottom = max(block['bbox'][3] for block in prev_line)
        curr_top = min(block['bbox'][1] for block in curr_line)
        y_gap = curr_top - prev_bottom
        
        # If the gap is too large, it's definitely a new paragraph
        if y_gap > 30:
            return False
            
        # Check for sentence continuation indicators
        prev_ends_sentence = prev_text.strip().endswith(('.', '!', '?', ':'))
        curr_starts_capital = curr_text.strip() and curr_text.strip()[0].isupper()
        curr_starts_list = curr_text.strip().startswith(('•', '-', '*')) or \
                          any(curr_text.strip().startswith(f"{n}.") for n in range(1, 10))
        
        # Continue paragraph if:
        # 1. Small gap AND
        # 2. Not end of sentence OR next line doesn't start with capital
        # 3. Not a list item
        return (y_gap <= 20 and 
                (not prev_ends_sentence or not curr_starts_capital) and
                not curr_starts_list)

    def get_text_with_bboxes(self, page_img_bytes, page_num: int, page_width: float, page_height: float) -> dict:
        """
        Extract text and bounding boxes from a PDF page using Google Cloud Vision API.
        """
        image = types.Image(content=page_img_bytes)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return {"text": "", "blocks": []}

        # Get full text
        full_text = texts[0].description
        
        # Create blocks from the word-level annotations
        word_blocks = []
        for text_block in texts[1:]:
            vertices = [(vertex.x, vertex.y) for vertex in text_block.bounding_poly.vertices]
            x_coords = [vertex[0] for vertex in vertices]
            y_coords = [vertex[1] for vertex in vertices]
            
            word_blocks.append({
                "text": text_block.description,
                "bbox": [min(x_coords), min(y_coords), max(x_coords), max(y_coords)],
                "page": page_num,
                "width": page_width,
                "height": page_height,
                "method": "google"
            })

        # Sort blocks by vertical position then horizontal
        sorted_blocks = sorted(word_blocks, key=lambda x: (x['bbox'][1], x['bbox'][0]))
        
        # Group words into lines
        lines = []
        current_line = []
        y_threshold = 12  # slightly more lenient
        
        for block in sorted_blocks:
            if not current_line:
                current_line.append(block)
                continue
                
            y_diff = abs(block['bbox'][1] - current_line[0]['bbox'][1])
            if y_diff <= y_threshold:
                current_line.append(block)
            else:
                current_line.sort(key=lambda x: x['bbox'][0])
                lines.append(current_line)
                current_line = [block]
        
        if current_line:
            current_line.sort(key=lambda x: x['bbox'][0])
            lines.append(current_line)

        # Group lines into paragraphs with improved continuation logic
        paragraphs = []
        current_paragraph = []
        
        for i, line in enumerate(lines):
            if not current_paragraph:
                current_paragraph.extend(line)
                continue
            
            prev_line = lines[i-1]
            if self.should_continue_paragraph(prev_line, line):
                current_paragraph.extend(line)
            else:
                # Finalize current paragraph
                x0 = min(block['bbox'][0] for block in current_paragraph)
                y0 = min(block['bbox'][1] for block in current_paragraph)
                x1 = max(block['bbox'][2] for block in current_paragraph)
                y1 = max(block['bbox'][3] for block in current_paragraph)
                
                text = ' '.join(block['text'] for block in current_paragraph)
                # Clean up spaces and handle hyphenation
                text = text.replace(' ,', ',').replace(' .', '.').replace(' !', '!').replace(' ?', '?')
                text = text.replace('- ', '-').replace(' -', '-')  # Handle hyphenation
                
                paragraphs.append({
                    'text': text,
                    'page': page_num,
                    'bbox': [x0, y0, x1, y1],
                    'width': page_width,
                    'height': page_height,
                    'method': 'google'
                })
                
                current_paragraph = list(line)

        # Add the last paragraph
        if current_paragraph:
            x0 = min(block['bbox'][0] for block in current_paragraph)
            y0 = min(block['bbox'][1] for block in current_paragraph)
            x1 = max(block['bbox'][2] for block in current_paragraph)
            y1 = max(block['bbox'][3] for block in current_paragraph)
            
            text = ' '.join(block['text'] for block in current_paragraph)
            text = text.replace(' ,', ',').replace(' .', '.').replace(' !', '!').replace(' ?', '?')
            text = text.replace('- ', '-').replace(' -', '-')
            
            paragraphs.append({
                'text': text,
                'page': page_num,
                'bbox': [x0, y0, x1, y1],
                'width': page_width,
                'height': page_height,
                'method': 'google'
            })

        return {
            "text": full_text,
            "blocks": paragraphs
        }