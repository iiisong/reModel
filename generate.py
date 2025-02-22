import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from PIL import Image
import numpy as np
import requests
from torchvision import transforms

def load_image(image_path):
    """Load and preprocess the image."""
    image = Image.open(image_path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor()
    ])
    return transform(image).unsqueeze(0)

def save_image(tensor, output_path):
    """Save the generated image."""
    image = transforms.ToPILImage()(tensor.squeeze(0))
    image.save(output_path)

def generate_decorated_room(input_image_path, prompt, output_image_path):
    """Generate a decorated room using ControlNet."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load ControlNet model
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-depth",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    # Load Stable Diffusion pipeline with ControlNet
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    
    # Load input image
    image = load_image(input_image_path).to(device)
    
    # Generate image with prompt
    output = pipe(prompt, image=image, num_inference_steps=30).images[0]
    
    # Save output image
    output.save(output_image_path)
    print(f"Decorated room saved to {output_image_path}")

# Example usage
input_image = "room_image.jpg"  # Change to your input image file
output_image = "decorated_room.jpg"
prompt = "A modern Scandinavian style decorated room with wooden furniture and warm lighting"
generate_decorated_room(input_image, prompt, output_image)