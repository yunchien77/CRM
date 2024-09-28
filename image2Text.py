import requests
from PIL import Image
from pillow_heif import register_heif_opener
from dotenv import load_dotenv
import os
import cv2
from requests.exceptions import RequestException
import time
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
        os.remove(input_file)  # 刪除原始文件
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
        #resized_path = os.path.splitext(img_path)[0] + "_resized.jpg"
        resized_image.save(img_path, quality=95)  # Save resized image
        print(f"Image resized to fit within {max_size_kb} KB and saved as {img_path}")
        return img_path

    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def ocr_image(img_path, ocr_engine, ocr_language, max_retries=3, timeout=30):
    original_path = img_path
    
    # 轉換HEIF到JPEG
    if os.path.splitext(img_path)[1].lower() in ['.heif', '.heic']:
        jpg_path = os.path.splitext(img_path)[0] + ".jpg"
        if convert_to_jpg(img_path, jpg_path):
            img_path = jpg_path
        else:
            return None, None

    # 調整圖像大小
    img_path = resize_image(img_path)
    if img_path != original_path and os.path.exists(original_path):
        os.remove(original_path)

    img = cv2.imread(img_path)

    if img is None:
        print("Error: Could not read the image.")
        return None, None

    # OCR API
    api_url = "https://api.ocr.space/parse/image"
    api_keys = [os.getenv('OCR_API_KEY'), os.getenv('OCR_API_KEY2')]

    # Image Compression & Conversion
    pil_image = Image.open(img_path)
    image_format = pil_image.format.lower()  

    if image_format in ['jpeg', 'jpg', 'png', 'bmp', 'gif']:  
        _, img_encoded = cv2.imencode('.' + image_format, img)
        files = {"file": ("image." + image_format, img_encoded.tobytes(), "image/" + image_format)}
        
        for api_key in api_keys:
            data = {
                "apikey": api_key,
                "OCREngine": ocr_engine,
                "language": ocr_language
            }

            for attempt in range(max_retries):
                try:
                    result = requests.post(api_url, files=files, data=data, timeout=timeout)
                    result.raise_for_status()  # 如果狀態碼不是200，會引發HTTPError
                    result_json = result.json()

                    if not result_json.get('IsErroredOnProcessing', False):
                        parsed_text = result_json['ParsedResults'][0]['ParsedText']
                        return parsed_text, img_path

                    print(f"Processing failed with API key. Trying next key if available.")
                    break  # 如果處理失敗但API有回應，跳出重試循環，嘗試下一個API key

                except requests.Timeout:
                    print(f"Timeout occurred. Attempt {attempt + 1} of {max_retries}")
                    if attempt == max_retries - 1:
                        print("Max retries reached. Moving to next API key.")
                        break
                    time.sleep(2 ** attempt)  # 指數退避

                except RequestException as e:
                    print(f"An error occurred: {e}")
                    if attempt == max_retries - 1:
                        print("Max retries reached. Moving to next API key.")
                        break
                    time.sleep(2 ** attempt)  # 指數退避

        print("Error: Processing failed with all available API keys.")
        return None, None

    else:
        print("Error: Unsupported or unknown image file format.")
        return None, None

# def ocr_image(img_path, ocr_engine, ocr_language):
#     original_path = img_path
    
#     # 轉換HEIF到JPEG
#     if os.path.splitext(img_path)[1].lower() in ['.heif', '.heic']:
#         jpg_path = os.path.splitext(img_path)[0] + ".jpg"
#         if convert_to_jpg(img_path, jpg_path):
#             img_path = jpg_path
#         else:
#             return None, None

#     # 調整圖像大小
#     img_path = resize_image(img_path)
#     if img_path != original_path and os.path.exists(original_path):
#         os.remove(original_path)

#     img = cv2.imread(img_path)

#     if img is None:
#         print("Error: Could not read the image.")
#         return None, None

#     # OCR API
#     api_url = "https://api.ocr.space/parse/image"
#     api_keys = [os.getenv('OCR_API_KEY'), os.getenv('OCR_API_KEY2')]

#     # Image Compression & Conversion
#     pil_image = Image.open(img_path)
#     # Detect image file type
#     image_format = pil_image.format.lower()  

#     if image_format in ['jpeg', 'jpg', 'png', 'bmp', 'gif']:  
#         # Convert image to byte stream
#         _, img_encoded = cv2.imencode('.' + image_format, img)
#         files = {"file": ("image." + image_format, img_encoded.tobytes(), "image/" + image_format)}
        
#         for api_key in api_keys:
#             data = {
#                 "apikey": api_key,
#                 "OCREngine": ocr_engine,
#                 "language": ocr_language
#             }

#             result = requests.post(api_url, files=files, data=data)
#             result_json = result.json()
#             print(result_json)

#             if not result_json.get('IsErroredOnProcessing', False):
#                 parsed_text = result_json['ParsedResults'][0]['ParsedText']
#                 return parsed_text, img_path

#             print(f"Processing failed with API key. Trying next key if available.")

#         print("Error: Processing failed with all available API keys.")
#         return None, None

#     else:
#         print("Error: Unsupported or unknown image file format.")
#         return None, None

def imageProcess(img_path):
    original_path = img_path
    
    # 轉換HEIF到JPEG
    if os.path.splitext(img_path)[1].lower() in ['.heif', '.heic']:
        jpg_path = os.path.splitext(img_path)[0] + ".jpg"
        if convert_to_jpg(img_path, jpg_path):
            img_path = jpg_path
        else:
            return None

    # 調整圖像大小
    img_path = resize_image(img_path)
    if img_path != original_path and os.path.exists(original_path):
        os.remove(original_path)

    return img_path