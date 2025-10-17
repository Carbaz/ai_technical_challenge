"""PDF Document Extraction module."""

# Thanks Grok Code Fast 1 for the base implementation idea.

import io
from logging import getLogger
from pathlib import Path

import pypdf
import pytesseract
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from PIL import Image, ImageEnhance

from app.config import OCR_DEBUG


class MyPDFLoader(BaseLoader):
    """Custom PDF loader that extracts text + applies OCR using CPU only."""

    def __init__(self, file_path: str):
        """Initialize with the PDF file path."""
        self.file_path = file_path

    def load(self):
        """Process a PDF file with text extraction + OCR, returns a Document per page."""
        _logger.info(f'LOADING PDF WITH OCR: {self.file_path}')
        page_texts = self._extract_text_and_ocr()
        return [Document(page_content=text.strip(), metadata={'source': self.file_path,
                                                              'Page': page_num})
                for page_num, text in enumerate(page_texts, start=1)
                if text.strip()]

    def _extract_text_and_ocr(self):
        """Extract text and OCR from PDF pages, return a list, a string per page."""
        page_texts = []
        try:
            with open(self.file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                for page_n, page in enumerate(pdf_reader.pages, start=1):
                    text = ''
                    # Step 1: Extract direct text from the page.
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
                    # Step 2: Apply OCR to images in the page.
                    page_ocr_text = self._extract_ocr_from_page(page, page_n)
                    if page_ocr_text:
                        text += page_ocr_text + '\n'
                    page_texts.append(text)
        except Exception as ex:
            _logger.error(f'ERROR PROCESSING {self.file_path}: {ex}')
        return page_texts

    def _extract_ocr_from_page(self, page, page_n):
        """Extract OCR text from images in a single page."""
        text = ''
        for img_n, image in enumerate(page.images, start=1):
            try:
                _logger.debug(f'PROCESSING PAGE {page_n} IMAGE {img_n} ({image.name})')
                img = Image.open(io.BytesIO(image.data))
                img_enhanced = image_enhance(img)
                ocr_text = pytesseract.image_to_string(
                    img_enhanced, config='--psm 11 --oem 3')
                if ocr_text.strip():
                    header = (f'Text extracted from file: "{Path(self.file_path).name}"'
                              f' image: "{image.name}" on page {page_n}:')
                    text += f'{header} {ocr_text}\n'
                    _logger.debug(f'OCR FROM PAGE {page_n} IMAGE {img_n} ({image.name}):'
                                  f'\n\t{text.strip()}')
                if OCR_DEBUG:
                    save_image_debug(img, img_enhanced, ocr_text, page_n, img_n)
            except Exception as ex:
                _logger.error(
                    f'OCR FAILED FOR PAGE {page_n} IMAGE {img_n} ({image.name}): {ex}')
        return text


def image_enhance(img):
    """Enhance image for better OCR results, handling transparency."""
    # If the image has transparency (RGBA), add a white background.
    if img.mode == 'RGBA':
        _logger.debug('IMAGE HAS TRANSPARENCY - ADDING WHITE BACKGROUND')
        # Create a white background of the same size.
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        # Paste the original image using the alpha channel as mask.
        background.paste(img, mask=img.split()[-1])
        # Convert to RGB (remove transparency).
        img = background.convert('RGB')
    _logger.debug('ENHANCING IMAGE FOR OCR')
    # Convert to grayscale.
    img = img.convert('L')
    # Increase contrast.
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    return img


def save_image_debug(image, image_enhanced, text, page_num, img_num):
    """Save image and extracted text for debugging."""
    debug_dir = Path('./ocr_debug')
    debug_dir.mkdir(parents=True, exist_ok=True)
    base_filename = debug_dir / f'page_{page_num}_img_{img_num}'
    _logger.info(f'SAVING IMAGE TO {base_filename}.png')
    image.save(f'{base_filename}.png')
    image_enhanced.save(f'{base_filename}_enhanced.png')
    _logger.info(f'SAVING OCR EXTRACTED TEXT TO {base_filename}.txt')
    with open(f'{base_filename}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text)


_logger = getLogger(__name__)
