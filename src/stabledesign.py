from PIL import Image
import requests
from io import BytesIO
import replicate

def stabledesign(img_fp: str, prompt: str) -> Image:
    input = {"prompt": prompt, "image_base": open(img_fp, "rb")}
    generated_image_url = replicate.run(
        "melgor/stabledesign_interiordesign:5e13482ea317670bfc797bb18bace359860a721a39b5bbcaa1ffcd241d62bca0",
        input=input
    )
    
    response = requests.get(generated_image_url)
    image_data = BytesIO(response.content)
    gen_image = Image.open(image_data)
    
    return gen_image