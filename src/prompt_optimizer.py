import openai
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

from src.utils import get_img_url

ITEMS_IN_IMAGE = """
In the room in the attached image, you have the following personal and furniture items: 

{items} 

"""

POTENTIAL_DECOR_TEXT_TEMPLATE = """
Please design a color scheme and list items that would suite the prompt found below in quotation marks. Do not provide explanations. Select items that could fit in the image attached as well.

"{user_description}"
"""

PROMPT_TEMPLATE = '''
{user_prompt}

The image contains the following objects at the following locations:
{image_objects}

Some potential decor items and colors that are suitable include but are not limited to:
{decor_ideas}
'''

def identify_objects(image: Image.Image) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and direct object identification assistant, focused on identifying objects in images of rooms."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                        Please identify all the furniture and decoration items in this room and return a list of them, their locations in the 
                        room relative to the camera, and their orientations. Be detailed regarding their locations and orientations. Provide 
                        them in the following format:
                        [Item: Item, Location: Location, Orientation: Orientation]
                    """
                },
                {
                    "type": "image_url",
                    "image_url": get_img_url(image)
                }
            ]
        }
    ]
    
    print("\n\nIdentifying objects in image via model query...\n\n")

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def optimize_prompt(image: Image.Image, user_desc: str, image_objects: bool = True) -> str:
    if image_objects :
        image_objects = ITEMS_IN_IMAGE.format(items=identify_objects(image))
    else :
        image_objects = ""
    
    optimization_query_prompt = image_objects + POTENTIAL_DECOR_TEXT_TEMPLATE.format(user_description=user_desc)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and creative interior design assistant, focused on providing recommendations for furniture and decoration items in rooms. You always list many options to give the user a wide range of choices. You always give at least three times as many recommendations as you may think is necessary."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": optimization_query_prompt
                },
                {
                    "type": "image_url",
                    "image_url": get_img_url(image)
                }
            ]
        }
    ]
    
    print(
    f'''
    Optimizing prompt with the following parameters:
    {optimization_query_prompt = }
    
    Awaiting response from OpenAI...
    ''')
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=400
    )
    
    prompt = PROMPT_TEMPLATE.format(
        user_prompt=user_desc,
        image_objects=image_objects,
        decor_ideas=response.choices[0].message.content
    )
    
    return prompt

if __name__ == "__main__":
    image_objects = identify_objects("test_data/input_img.png")
    optimize_prompt("input_img.png", "A cozy and warm plant person's room with a lot of natural light and books.", image_objects)