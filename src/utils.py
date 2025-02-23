import base64
from io import BytesIO
from PIL import Image

def get_img_url(img: Image) -> dict:
    """
    Get the image URL for the OpenAI API.

    Parameters:
        img (Image): The image to encode.

    Returns:
        dict: The image URL.
    """
    OPENAI_IMG_URL_TEMPLATE = "data:image/{file_extension};base64,{base64_image}"
    
    return {
        "url": OPENAI_IMG_URL_TEMPLATE.format(
            file_extension='png',
            base64_image=process_image(img)
        )
    }

def process_image(image: Image.Image, max_size: int=1025) -> str:
    """
    Process an image from a given path, encoding it in base64. If the image is a PNG and smaller than max_size,
    it encodes the original. Otherwise, it resizes and converts the image to PNG before encoding.

    Parameters:
        path (str): The file path to the image.
        max_size (int): The maximum width and height allowed for the image.

    Returns:
        Tuple[str, int]: A tuple containing the base64-encoded image and the size of the largest dimension.
    """
    width, height = image.size
    if not (image.format == "PNG" and width <= max_size and height <= max_size):
        image = resize_image(image, max_size)
        
    png_image = convert_to_png(image)
    return base64.b64encode(png_image).decode('utf-8')

def resize_image(image: Image.Image, max_dimension: int) -> Image.Image:
    """
    Resize a PIL image to ensure that its largest dimension does not exceed max_size.

    Parameters:
        image (Image.Image): The PIL image to resize.
        max_size (int): The maximum size for the largest dimension.

    Returns:
        Image.Image: The resized image.
    """
    width, height = image.size

    # Check if the image has a palette and convert it to true color mode
    if image.mode == "P":
        if "transparency" in image.info:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.LANCZOS)
    
    return image

def convert_to_png(image: Image.Image) -> bytes:
    """
    Convert a PIL Image to PNG format.

    Parameters:
        image (Image.Image): The PIL image to convert.

    Returns:
        bytes: The image in PNG format as a byte array.
    """
    with BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()
    
if __name__ == "__main__":
    img = Image.open("test_data/base_room.png")
    get_img_url(img)