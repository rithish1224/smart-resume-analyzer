import io
import logging
from typing import Tuple
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from backend.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Configure Tesseract path if provided in settings
        if getattr(settings, "TESSERACT_CMD", None):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def extract_text(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Extract text from an image using pytesseract.
        Returns a tuple of (extracted_text, confidence_score).
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Pre-processing
            # 1. Convert to grayscale
            image = image.convert("L")
            # 2. Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            # 3. Denoise
            image = image.filter(ImageFilter.MedianFilter())
            
            # Extract text data
            config = "--psm 6"
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate confidence
            confidences = [int(conf) for conf in data["conf"] if str(conf).isdigit() and int(conf) >= 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            threshold = getattr(settings, "OCR_CONFIDENCE_THRESHOLD", 50.0)
            if avg_confidence < threshold:
                logger.warning(f"Low OCR confidence: {avg_confidence}% (Threshold: {threshold}%)")
                
            text = pytesseract.image_to_string(image, config=config)
            return text, avg_confidence
            
        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract not found. Please install tesseract-ocr and set TESSERACT_CMD in settings.")
            return "", 0.0
        except Exception as e:
            logger.error(f"OCR Processing error: {str(e)}")
            return "", 0.0
