"""PDF Document Extraction module."""

# Thanks Grok Code Fast 1 for the base implementation idea:

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
        """Load and process a single PDF file with text extraction + OCR."""
        _logger.info(f"LOADING PDF WITH OCR: {self.file_path}")
        text = self._extract_text_and_ocr()
        if text.strip():
            return [Document(page_content=text.strip(),
                             metadata={"source": self.file_path})]
        return []

    def _extract_text_and_ocr(self):
        """Extract text from PDF pages and apply OCR to images."""
        _logger.info(f"EXTRACTING TEXT AND APPLYING OCR FOR: {self.file_path}")
        text = ""
        try:
            # Step 1: Extract text directly from PDF
            text += self._extract_direct_text()
            # Step 2: Apply OCR to images
            text += "\n" + self._extract_ocr_text()
        except Exception as ex:
            _logger.warning(f"Error processing {self.file_path}: {ex}")
        return text

    def _extract_direct_text(self):
        """Extract text directly from PDF pages."""
        _logger.info(f"EXTRACTING DIRECT TEXT FROM PDF: {self.file_path}")
        text = ""
        with open(self.file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_ocr_text(self):
        """Extract text from PDF images using OCR."""
        _logger.info(f'APPLYING OCR TO IMAGES IN PDF: {self.file_path}')
        text = ""
        try:
            with open(self.file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                for page_n, page in enumerate(pdf_reader.pages, start=1):
                    for img_n, image in enumerate(page.images, start=1):
                        try:
                            img = Image.open(io.BytesIO(image.data))
                            img_enhanced = _image_enhance(img)
                            ocr_text = pytesseract.image_to_string(
                                img_enhanced, config='--psm 11 --oem 3')
                            if ocr_text.strip():
                                text += ocr_text + '\n'
                            _logger.info(f'OCR extracted\n\t"{ocr_text.strip()}"')
                        except Exception as img_error:
                            _logger.warning(
                                f'OCR FAILED FOR IMAGE IN {self.file_path}: {img_error}')
                        else:
                            if OCR_DEBUG:
                                _save_image_debug(img, img_enhanced, ocr_text,
                                                  page_n, img_n)
        except Exception as ex:
            _logger.warning(f'OCR SETUP FAILED FOR {self.file_path}: {ex}')
        return text


def _image_enhance(img):
    """Enhance image for better OCR results, handling transparency."""
    # If the image has transparency (RGBA), add a white background.
    if img.mode == 'RGBA':
        # Create a white background of the same size.
        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
        # Paste the original image using the alpha channel as mask.
        background.paste(img, mask=img.split()[-1])
        # Convert to RGB. (remove transparency)
        img = background.convert('RGB')
    # Convert to grayscale.
    img = img.convert('L')
    # Increase contrast.
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    return img


def _save_image_debug(image, image_enhanced, text, page_num, img_num):
    """Save image and extracted text for debugging."""
    debug_dir = Path('./ocr_debug')
    debug_dir.mkdir(parents=True, exist_ok=True)
    base_filename = debug_dir / f'page_{page_num}_img_{img_num}'
    _logger.info(f'SAVING IMAGE TO {base_filename}.png')
    image.save(f'{base_filename}.png')
    image_enhanced.save(f'{base_filename}_enhanced.png')
    _logger.info(f'SAVE OCR EXTRACTED\n\t"{text.strip()}"')
    with open(f'{base_filename}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text)


# Instantiate local logger.
_logger = getLogger(__name__)
