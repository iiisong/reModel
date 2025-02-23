from PIL import Image
import requests
import replicate

import base64
from io import BytesIO


OPENAI_IMG_URL_TEMPLATE = "data:image/{file_extension};base64,{base64_image}"

def stabledesign(input_image: Image.Image, prompt: str) -> Image.Image :
    buffered = BytesIO()
    input_image.save(buffered, format="PNG")
    input_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # input_i = {"prompt": prompt, "image_base": input_img_str}
    input_i = {"prompt": prompt, "image_base": OPENAI_IMG_URL_TEMPLATE.format(
                        file_extension='png',
                        base64_image=input_img_str
                    )}
    
    
    generated_image_url = replicate.run(
        "melgor/stabledesign_interiordesign:5e13482ea317670bfc797bb18bace359860a721a39b5bbcaa1ffcd241d62bca0",
        input=input_i
    )
    
    response = requests.get(generated_image_url)
    image_data = BytesIO(response.content)
    gen_image = Image.open(image_data)
    
    return gen_image


def save_image(img: Image, save_path: str):
    img.save(save_path)
    
    return save_path