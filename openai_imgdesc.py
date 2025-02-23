import openai
import dotenv
import os
import base64

dotenv.load_dotenv()
OPENAI_IMG_URL_TEMPLATE = "data:image/{file_extension};base64,{base64_image}"

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def query_image_objects(img_path: str) -> str :
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise Exception("API key is required")


    input_image_path = img_path
    base64_image = encode_image(input_image_path)
    
    image_data_url = OPENAI_IMG_URL_TEMPLATE.format(
        file_extension=input_image_path.split('.')[-1],
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

    print(response)
    print()
    print(response.choices[0].message.content)
    
    return response.choices[0].message.content




if __name__ == "__main__":
    query_image_objects("input_img.png")