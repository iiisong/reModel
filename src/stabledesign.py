from PIL import Image
import requests
import replicate

import base64
from io import BytesIO

import dotenv

import openai_imgdesc as oai
import stabledesign as sd


OPENAI_IMG_URL_TEMPLATE = "data:image/{file_extension};base64,{base64_image}"
dotenv.load_dotenv()

def stabledesign(input_image: Image.Image, prompt: str, additional_settings: dict = None) -> Image.Image :
    buffered = BytesIO()
    input_image.save(buffered, format="PNG")
    input_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    if additional_settings is None :
        additional_settings = {
            # TODO
        }
    
    # input_i = {"prompt": prompt, "image_base": input_img_str}
    input_i = {
            "prompt": prompt,
            "image_base": OPENAI_IMG_URL_TEMPLATE.format(
                file_extension='png',
                base64_image=input_img_str
            )
        }
    
    if additional_settings:
        input_i.update(additional_settings)
    
    
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





PROMPT_TEMPLATE = '''
{user_prompt}

The image contains the following objects at the following locations:
{image_objects}

Some potential decor items and colors that are suitable include but are not limited to:
{decor_ideas}
'''


'''
Observations
strength: how much change
num_steps: how many iterations
guidance_scale: how closely to follow the input image

General:
8 < guidance scale < 70 (honestly morelike 20)
strength below 0.5?
'''

import random
if __name__ == "__main__":
    add_sets = [
        # {"strength": round(random.random(), 2), "num_steps": random.randint(5,100), "guidance_scale": random.randint(1,100)}
        # {"strength": round(random.random() / 2, 2) + 0.3, "num_steps": 50, "guidance_scale": random.randint(1,50)}
        {"strength": 0.9, "num_steps": 50, "guidance_scale": 10}
        for x in range(10)
    ]
    for r in add_sets :
        print(f'{r = }')
    # add_sets = [
    #     # {"strength": 0.9, "num_steps": 10, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 20, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 30, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 40, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 60, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 70, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 80, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 90, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 100, "guidance_scale": 10},
        
        
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 1},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 2},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 9},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 10},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 11},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 20},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 21},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 40},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 41},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 90},
    #     # {"strength": 0.9, "num_steps": 50, "guidance_scale": 91},
        
        
        
    #     {"strength": 0.3, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.4, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.5, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.6, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.7, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.8, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 0.9, "num_steps": 50, "guidance_scale": 10},
    #     {"strength": 1.0, "num_steps": 50, "guidance_scale": 10},
    # ]
    
    input_img_name = 'base_room.png'
    input_img = Image.open(f"test_data/{input_img_name}")
    prompt = 'Cottage core college dorm for a plant and book lover.'
    
    image_objs = oai.query_image_objects(input_img)
    
    decor_ideas = oai.query_potential_decor_ideas(input_img, prompt, image_objs)
    
    prompt = PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        image_objects=image_objs,
        decor_ideas=decor_ideas
    )
    
    print(f'Prompt: \n{prompt}\n=======\n')
    
    import time
    times_taken = []
    for i, add_set in enumerate(add_sets):
        
        timeit_start = time.time()
        output = stabledesign(input_img, prompt, add_set)
        time_end = time.time()
        time_diff = round(time_end - timeit_start, 3)
        
        times_taken.append(f"{time_diff:<15}s taken for {add_set = }")
        
        file_name = f"{i}{input_img_name}_strength-{add_set['strength']}_num_steps-{add_set['num_steps']}_guidance_scale-{add_set['guidance_scale']}.png"
        # file_name = f"{input_img_name}_strength-{add_set['strength']}_num_steps-{add_set['num_steps']}_guidance_scale-{add_set['guidance_scale']}.png"
        output.save(f"test_data/outputs/{file_name}")
        print(f"Generated image saved: {file_name}")
        
    for i, add_set in enumerate(add_sets):
        
        timeit_start = time.time()
        output = stabledesign(input_img, 'This is a test description', add_set)
        time_end = time.time()
        time_diff = round(time_end - timeit_start, 3)
        
        times_taken.append(f"{time_diff:<15}s taken for {add_set = }")
        
        file_name = f"{i}testdesc{input_img_name}_strength-{add_set['strength']}_num_steps-{add_set['num_steps']}_guidance_scale-{add_set['guidance_scale']}.png"
        output.save(f"test_data/outputs/{file_name}")
        print(f"Generated image saved: {file_name}")
        
    print()
    for r in times_taken :
        print(r)