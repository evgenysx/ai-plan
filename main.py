from openai import OpenAI
import datetime
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

# итаем чертеж
base64_image = encode_image("docs/plan_ai.jpg")

# Then pass it to the API
# "url": base64_image

# распознать изображение
start = datetime.datetime.now()
print('Время старта: ' + str(start))

with open('keys/test.txt', 'r') as file:
    apikey = file.readline()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=apikey,
)
response = client.chat.completions.create(
    model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    messages=[
        {
            "role": "user", 
            "content": [
            {
                "type": "text",
                "text": "parse table in this image"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": base64_image
                }
            }
            ]
        },
        
    ],
)
finish = datetime.datetime.now()
print('Время работы: ' + str(finish - start))

msg = response.choices[0].message
print(getattr(msg, "content", None))

