#!/usr/bin/env python3
"""
Extract individual check images from a scanned check deposit PDF.

This script converts each PDF page to a high-resolution image, detects
individual check/deposit-slip regions using contour analysis, and saves
each as a separate numbered image file. It also runs OCR on each region
to produce a companion text file that aids Claude's visual extraction.

Usage:
    python3 extract_checks.py <input_pdf> <output_dir> [--dpi 300]

Output:
    output_dir/
        page_1.png                      # Full page image
        check_001.png                   # Individual check image
        check_001_ocr.txt               # OCR text for that check
        check_001_payer_detail.png      # Zoomed 2x crop of payer region
        check_001_payer_ocr.txt         # OCR of zoomed payer region
        check_001_amount_detail.png     # Zoomed 2x crop of amount region
        check_001_amount_ocr.txt        # OCR of zoomed amount region
        ...
        manifest.json                   # Summary of all detected checks
"""

import argparse
import json
import os
import sys

def install_dependencies():
    """Ensure required packages are available."""
    required = {
        'pdf2image': 'pdf2image',
        'PIL': 'Pillow',
        'cv2': 'opencv-python-headless',
        'pytesseract': 'pytesseract',
        'numpy': 'numpy',
    }
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        import subprocess
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install',
            '--break-system-packages', '-q'
        ] + missing)


def convert_pdf_to_images(pdf_path, dpi=300):
    """Convert PDF pages to PIL images."""
    from pdf2image import convert_from_path
    return convert_from_path(pdf_path, dpi=dpi)


def detect_check_regions(pil_image, min_width=400, min_height=200):
    """
    Detect individual check/document regions on a page image.

    Uses morphological operations to merge nearby content into blobs,
    then finds bounding rectangles that are large enough to be checks.

    Returns list of (x, y, width, height) tuples sorted top-to-bottom,
    left-to-right.
    """
    import cv2
    import numpy as np

    # Convert PIL to OpenCV
    img_array = np.array(pil_image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Threshold: content is dark on light background
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)

    # Dilate aggressively to merge nearby text/lines into solid blobs
    kernel = np.ones((30, 30), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=3)

    # Find contours of merged regions
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        if cw >= min_width and ch >= min_height:
            regions.append((x, y, cw, ch))

    # Sort by row position (y // 200 groups into rows), then left-to-right
    regions.sort(key=lambda r: (r[1] // 200, r[0]))
    return regions


def classify_check_type(ocr_text):
    """
    Classify the type of document based on OCR text content.

    Returns one of:
        'personal_check' - Standard personal check with payer info printed
        'bill_pay_check' - Bank-issued bill pay / remittance check
        'cash_deposit'   - Cash-in-debit or deposit slip
        'check_back'     - Back/endorsement side of a check
        'unknown'        - Could not determine type
    """
    text_lower = ocr_text.lower()

    if 'cash in' in text_lower and 'debit' in text_lower:
        return 'cash_deposit'
    if 'virtual document' in text_lower and 'cash drawer' in text_lower:
        return 'cash_deposit'
    if 'for deposit only' in text_lower or 'pay to the order' in text_lower:
        if 'pay ' not in text_lower[:200].lower():
            return 'check_back'
    if 'please post this payment' in text_lower or 'mutual customer' in text_lower:
        return 'bill_pay_check'
    if 'pay ' in text_lower and ('dollars' in text_lower or 'order of' in text_lower):
        return 'personal_check'

    return 'unknown'


def ocr_image(pil_image):
    """Run Tesseract OCR on a PIL image and return the text."""
    import pytesseract
    return pytesseract.image_to_string(pil_image)


def create_detail_crops(pil_image, check_id, output_dir):
    """
    Create zoomed detail crops of key check regions for better readability.

    Bank check scans are often dense, and when the full check is viewed at
    normal size, small text (especially payer names and addresses on bill-pay
    checks) can be too tiny to read accurately. This function crops and
    upscales specific regions where critical fields live.

    Produces:
        {check_id}_payer_detail.png  - Top-left ~45% of check, 2x upscaled
        {check_id}_amount_detail.png - Top-right ~45% of check, 2x upscaled
        {check_id}_payer_ocr.txt     - OCR of the zoomed payer region
        {check_id}_amount_ocr.txt    - OCR of the zoomed amount region

    Returns dict with paths and OCR text for the detail crops.
    """
    from PIL import Image
    import pytesseract

    w, h = pil_image.size
    details = {}

    # The check face (front) is typically the top ~60% of the image
    # (bottom portion is often the deposit strip or back-of-check image)
    face_h = int(h * 0.6)

    # Payer region: top-left quadrant of the check face
    # This is where payer name, address, phone, and memo appear
    payer_crop = pil_image.crop((0, 0, int(w * 0.45), face_h))
    payer_upscaled = payer_crop.resize(
        (payer_crop.width * 2, payer_crop.height * 2), Image.LANCZOS
    )
    payer_path = os.path.join(output_dir, f'{check_id}_payer_detail.png')
    payer_upscaled.save(payer_path)
    payer_ocr = pytesseract.image_to_string(payer_upscaled)
    payer_ocr_path = os.path.join(output_dir, f'{check_id}_payer_ocr.txt')
    with open(payer_ocr_path, 'w') as f:
        f.write(payer_ocr)
    details['payer_detail'] = f'{check_id}_payer_detail.png'
    details['payer_ocr_file'] = f'{check_id}_payer_ocr.txt'
    details['payer_ocr_text'] = payer_ocr.strip()

    # Amount/date region: top-right quadrant of the check face
    # This is where the amount, date, check number, and payee appear
    amount_crop = pil_image.crop((int(w * 0.40), 0, w, face_h))
    amount_upscaled = amount_crop.resize(
        (amount_crop.width * 2, amount_crop.height * 2), Image.LANCZOS
    )
    amount_path = os.path.join(output_dir, f'{check_id}_amount_detail.png')
    amount_upscaled.save(amount_path)
    amount_ocr = pytesseract.image_to_string(amount_upscaled)
    amount_ocr_path = os.path.join(output_dir, f'{check_id}_amount_ocr.txt')
    with open(amount_ocr_path, 'w') as f:
        f.write(amount_ocr)
    details['amount_detail'] = f'{check_id}_amount_detail.png'
    details['amount_ocr_file'] = f'{check_id}_amount_ocr.txt'
    details['amount_ocr_text'] = amount_ocr.strip()

    return details


def extract_checks(pdf_path, output_dir, dpi=300):
    """
    Main extraction pipeline.

    1. Convert PDF pages to images
    2. Detect check regions on each page
    3. Crop and save each check
    4. Run OCR on each check
    5. Write manifest.json with metadata
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Converting {pdf_path} to images at {dpi} DPI...")
    pages = convert_pdf_to_images(pdf_path, dpi=dpi)
    print(f"  Found {len(pages)} page(s)")

    manifest = {
        'source_pdf': os.path.basename(pdf_path),
        'dpi': dpi,
        'total_pages': len(pages),
        'checks': []
    }

    check_num = 0
    for page_idx, page_img in enumerate(pages):
        page_num = page_idx + 1
        print(f"\nProcessing page {page_num}...")

        # Save full page
        page_path = os.path.join(output_dir, f'page_{page_num}.png')
        page_img.save(page_path)

        # Detect check regions
        regions = detect_check_regions(page_img)
        print(f"  Detected {len(regions)} check region(s)")

        w, h = page_img.size
        for x, y, cw, ch in regions:
            check_num += 1
            check_id = f'check_{check_num:03d}'

            # Crop with padding
            pad = 10
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(w, x + cw + pad)
            y2 = min(h, y + ch + pad)
            crop = page_img.crop((x1, y1, x2, y2))

            # Save check image
            img_path = os.path.join(output_dir, f'{check_id}.png')
            crop.save(img_path)

            # Run OCR
            ocr_text = ocr_image(crop)
            ocr_path = os.path.join(output_dir, f'{check_id}_ocr.txt')
            with open(ocr_path, 'w') as f:
                f.write(ocr_text)

            # Classify document type
            doc_type = classify_check_type(ocr_text)

            # Create zoomed detail crops of payer and amount regions
            # These 2x-upscaled crops make small text (especially payer
            # names on bill-pay checks) much easier to read visually
            detail_info = create_detail_crops(crop, check_id, output_dir)

            manifest['checks'].append({
                'id': check_id,
                'page': page_num,
                'region': {'x': x, 'y': y, 'width': cw, 'height': ch},
                'image': f'{check_id}.png',
                'ocr_file': f'{check_id}_ocr.txt',
                'type': doc_type,
                'ocr_preview': ocr_text[:200].strip(),
                'details': detail_info
            })

            print(f"  {check_id}: {doc_type} ({crop.size[0]}x{crop.size[1]})")

    manifest['total_checks'] = check_num

    # Write manifest
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nExtraction complete: {check_num} check(s) saved to {output_dir}")
    print(f"Manifest: {manifest_path}")
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract check images from scanned PDF')
    parser.add_argument('input_pdf', help='Path to the check deposit PDF')
    parser.add_argument('output_dir', help='Directory to save extracted check images')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF conversion (default: 300)')
    args = parser.parse_args()

    install_dependencies()
    extract_checks(args.input_pdf, args.output_dir, dpi=args.dpi)
