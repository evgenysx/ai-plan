from core.ai import ai_image_request
from core.image import encode_image


def parse_plan(base64_image) :
    return ai_image_request(base64_image, "parse table in this image")