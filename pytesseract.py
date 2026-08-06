"""Lightweight shim for pytesseract used in smoke runs when actual tesseract is not available.
This returns empty OCR results to keep flow running.
"""
import sys

# provide a pytesseract attribute like the real package
this = sys.modules[__name__]
pytesseract = this

# path placeholder
tesseract_cmd = ''

# simple image_to_string stub
def image_to_string(image, config=None):
    # return empty string (no digits found) so callers treat as 0
    return ''
