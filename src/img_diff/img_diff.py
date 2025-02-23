from openai import OpenAI
from utils import process_image

client = OpenAI()

def img_diff(base_img, gen_img):
    
    prompt: str = ' '.join([
        "Compare these two images of the rooms and list everything in the second room that is missing from the first decorated one.",
        "from the empty one.\n\n",
        "Output in a comma separated list like:\n",
        "> White Curtains, Bedsheets, Office Chair"
    ])
    
    base_img_b64: bytes = process_image(base_img)[0]
    gen_img_b64 = process_image(gen_img)[0]
    
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text", 
                        "text": prompt
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{base_img_b64}"}
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{gen_img_b64}"}
                    },
                ]
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    base_img = "src/img_diff/test_data/base_room.png"
    gen_img = "src/img_diff/test_data/gen_room.png"
    print(img_diff(base_img, gen_img))