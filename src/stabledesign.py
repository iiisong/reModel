from PIL import Image
import requests
import replicate

from io import BytesIO

from src.prompt_optimizer import optimize_prompt
from src.utils import get_img_url

STABLE_DESIGN_MODEL_ID = "melgor/stabledesign_interiordesign:5e13482ea317670bfc797bb18bace359860a721a39b5bbcaa1ffcd241d62bca0"

ADDITIONAL_PARAMS = {
    'guidance_scale': 20,       # default 10
    'num_steps': 50,            # default 50
    'strength': 0.6             # default 0.9
}

def stabledesign(input_image: Image.Image, prompt: str, optimize: bool=True) -> Image.Image:
    params = {
        "prompt": optimize_prompt(input_image, prompt) if optimize else prompt, 
        "image_base": get_img_url(input_image)['url'],
    }
    
    params.update(ADDITIONAL_PARAMS)
    
    generated_image_url = replicate.run(
        STABLE_DESIGN_MODEL_ID,
        input=params
    )
    
    response = requests.get(generated_image_url)
    image_data = BytesIO(response.content)
    gen_image = Image.open(image_data)
    
    return gen_image


def save_image(img: Image.Image, save_path: str):
    img.save(save_path)
    
    return save_path

if __name__ == "__main__":
    base_img = "test_data/input_img.png"
    gen_img_path = "test_data/OUTPUT.png"
    prompt = 'Cottage core college dorm for a plant and book lover.'

    input_image = Image.open(base_img)

    output = stabledesign(input_image, prompt, optimize=True)
    output.save(gen_img_path)