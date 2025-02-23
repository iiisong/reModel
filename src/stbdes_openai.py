import openai_imgdesc as oai
import stabledesign as sd
import os


PROMPT_TEMPLATE = '''
{user_prompt}

The image contains the following objects at the following locations:
{image_objects}

Some potential decor items and colors that are suitable include but are not limited to:
{decor_ideas}
'''

def query_redesign(base_img_path: str, user_prompt: str, output_path: str) -> str:    
    image_objs = oai.query_image_objects(base_img_path)
    print(f'Objects: {image_objs}\n')
    
    decor_ideas = oai.query_potential_decor_ideas(base_img_path, "This is a test description", image_objs)
    print(f'Decor Ideas: {decor_ideas}\n')

    
    output = sd.stabledesign(base_img_path, PROMPT_TEMPLATE.format(
        user_prompt=user_prompt,
        image_objects=image_objs,
        decor_ideas=decor_ideas
    ))
    
    sd.save_image(output, output_path)
    
    return output_path


if __name__ == "__main__":
    base_img = "../input_img.png"
    gen_img_path = "../output_img.png"
    
    prompt = 'Cottage core college dorm for a plant and book lover.'

    # print(os.listdir("../"))
    
    prompt = 'Cottage core college dorm for a plant and book lover.'

    query_redesign(base_img, prompt, gen_img_path)
    print(f'Generated image saved at: {gen_img_path}')