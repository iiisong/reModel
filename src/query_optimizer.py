import openai

from dotenv import load_dotenv
load_dotenv()

from utils import process_image, OPENAI_IMG_URL_TEMPLATE

ITEMS_IN_IMAGE = """
In the room in the attached image, you have the following personal and furniture items: 

{items} 

"""
POTENTIAL_DECOR_TEXT_TEMPLATE = """
Please design a color scheme and list items that would suite the prompt found below in quotation marks. Do not provide explanations. Select items that could fit in the image attached as well.

"{user_description}"
"""

def identify_objects(img_path: str) -> str :
    base64_image = process_image(img_path)[0]
    
    image_data_url = OPENAI_IMG_URL_TEMPLATE.format(
        file_extension=img_path.split('.')[-1],
        base64_image=base64_image
    )

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
                    "image_url": {"url": image_data_url}
                }
            ]
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=150
    )
    
    return response.choices[0].message.content

def optimize_query(img_path: str, user_desc: str, query_img_objects: str = None) -> str:
    objects = identify_objects(img_path)
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
                    "text": ('' if not objects else ITEMS_IN_IMAGE.format(items=objects)) + POTENTIAL_DECOR_TEXT_TEMPLATE.format(user_description=user_desc)
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": OPENAI_IMG_URL_TEMPLATE.format(
                            file_extension=img_path.split('.')[-1],
                            base64_image=process_image(img_path)[0]
                        )
                    }
                }
            ]
        }
    ]
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=400
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    objects = identify_objects("test_data/input_img.png")
    optimize_query("input_img.png", "A cozy and warm plant person's room with a lot of natural light and books.", objects)