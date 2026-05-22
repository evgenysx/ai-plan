from openai import OpenAI


# Then pass it to the API
# "url": base64_image



with open('keys/mykey.txt', 'r') as file:
    apikey = file.readline()


def ai_image_request(base64_image, question):
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
                    "text": question
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
    msg = response.choices[0].message
    return msg