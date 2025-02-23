import base64, time, io
from PIL import Image
from typing import Tuple

OPENAI_IMG_URL_TEMPLATE = "data:image/{file_extension};base64,{base64_image}"

def process_image(path: str, max_size: int=1025) -> Tuple[str, int]:
    """
    Process an image from a given path, encoding it in base64. If the image is a PNG and smaller than max_size,
    it encodes the original. Otherwise, it resizes and converts the image to PNG before encoding.

    Parameters:
        path (str): The file path to the image.
        max_size (int): The maximum width and height allowed for the image.

    Returns:
        Tuple[str, int]: A tuple containing the base64-encoded image and the size of the largest dimension.
    """
    with Image.open(path) as image:
        width, height = image.size
        mimetype = image.get_format_mimetype()
        if mimetype == "image/png" and width <= max_size and height <= max_size:
            with open(path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
                return (encoded_image, max(width, height))
        else:
            resized_image = resize_image(image, max_size)
            png_image = convert_to_png(resized_image)
            return (base64.b64encode(png_image).decode('utf-8'),
                    max(width, height)  # same tuple metadata
                   )

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
        
        timestamp = time.time()

    return image

def convert_to_png(image: Image.Image) -> bytes:
    """
    Convert a PIL Image to PNG format.

    Parameters:
        image (Image.Image): The PIL image to convert.

    Returns:
        bytes: The image in PNG format as a byte array.
    """
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        return output.getvalue()


def create_image_content(image, maxdim, detail_threshold):
    detail = "low" if maxdim < detail_threshold else "high"
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{image}", "detail": detail}
    }