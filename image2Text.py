import requests
from PIL import Image
#import numpy as np
from pillow_heif import register_heif_opener
from dotenv import load_dotenv
import os
import cv2

register_heif_opener()
load_dotenv()

jpg_path = "output_image.jpg"

def convert_to_jpg(input_file, output_file):
    try:
        img = Image.open(input_file)
        img = img.convert("RGB")
        img.save(output_file, "JPEG", quality=95)
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file} to {output_file}: {e}")
        return False

def resize_image(img_path, max_size_kb=1024):
    try:
        # Check current file size
        current_size_kb = os.path.getsize(img_path) / 1024
        if current_size_kb <= max_size_kb:
            return img_path  # Return original path if within limit

        # Open original image
        pil_image = Image.open(img_path)
        width, height = pil_image.size

        # Calculate resize ratio to fit within max_size_kb
        resize_ratio = (max_size_kb * 1024) / os.path.getsize(img_path)
        new_width = int(width * resize_ratio)
        new_height = int(height * resize_ratio)

        # Resize image using Lanczos resampling (recommended alternative to ANTIALIAS)
        resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        resized_path = os.path.splitext(img_path)[0] + "_resized.jpg"
        resized_image.save(resized_path, quality=95)  # Save resized image
        print(f"Image resized to fit within {max_size_kb} KB and saved as {resized_path}")
        return resized_path

    except Exception as e:
        print(f"Error resizing image: {e}")
        return None


def ocr_image(img_path):
    # Convert HEIF to JPEG if needed
    if os.path.splitext(img_path)[1].lower() in ['.heif', '.heic']:
        jpg_path = os.path.splitext(img_path)[0] + ".jpg"
        if not convert_to_jpg(img_path, jpg_path):
            return None
        img_path = jpg_path

    img_path = resize_image(img_path)
    img = cv2.imread(img_path)

    if img is None:
        print("Error: Could not read the image.")
        return None

    # OCR API
    api_url = "https://api.ocr.space/parse/image"
    api_key = os.getenv('OCR_API_KEY')

    # Image Compression & Conversion
    pil_image = Image.open(img_path)
    # Detect image file type
    image_format = pil_image.format.lower()  

    if image_format in ['jpeg', 'jpg', 'png', 'bmp', 'gif']:  
        # Convert image to byte stream
        _, img_encoded = cv2.imencode('.' + image_format, img)
        files = {"file": ("image." + image_format, img_encoded.tobytes(), "image/" + image_format)}
        data = {
            "apikey": api_key,
            "OCREngine": 2, # engine 1(multi-language) or 2(character)
            "language": 'cht',  # default: eng
            #"isOverlayRequired": True   # provide location info
        }

        # POST to OCR.space API
        result = requests.post(api_url, files=files, data=data)

        # Get the OCR result as JSON
        result_json = result.json()
        print(result_json)
        os.removedirs('CRM/img/')

        parsed_text = result_json['ParsedResults'][0]['ParsedText']
        return parsed_text

    else:
        print("Error: Unsupported or unknown image file format.")
        return None