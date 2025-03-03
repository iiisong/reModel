# import __openai_imgdesc as oai
from prompt_optimizer import optimize_prompt, identify_objects
from stabledesign import stabledesign
import os

from PIL import Image

PROMPT_TEMPLATE = '''
{user_prompt}

The image contains the following objects at the following locations:
{image_objects}

Some potential decor items and colors that are suitable include but are not limited to:
{decor_ideas}
'''

def query_redesign(input_image: Image.Image, user_prompt: str) -> Image.Image :    
    image_objs = identify_objects(input_image)
    # print(f'Objects: {image_objs}\n')
    
    decor_ideas = optimize_prompt(input_image, user_prompt, image_objs)
    # print(f'Decor Ideas: {decor_ideas}\n')
    
    output = stabledesign(input_image, PROMPT_TEMPLATE.format(
        user_prompt=user_prompt,
        image_objects=image_objs,
        decor_ideas=decor_ideas
    ))
    
    # sd.save_image(output, output_path)
    
    return output


if __name__ == "__main__":
    base_img = "test_data/base_room.png"
    gen_img_path = "test_data/OUTPUT.png"
    
    prompt = 'Cottage core college dorm for a plant and book lover.'

    # print(os.listdir("../"))
    input_image = Image.open(base_img)
    
    prompt = 'Cottage core college dorm for a plant and book lover.'


    output = query_redesign(input_image, prompt)
    
    output.save(gen_img_path)

    # query_redesign(base_img, prompt, gen_img_path)
    # print(f'Generated image saved at: {gen_img_path}')