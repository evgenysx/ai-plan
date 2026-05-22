import base64
from mimetypes import guess_type

# читает локальный файл и кодирует в base64
def encode_image(image_path):
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{base64_encoded_data}"