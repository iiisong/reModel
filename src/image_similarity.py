import torch
import clip
from PIL import Image

# Load the CLIP model
model, preprocess = clip.load("ViT-B/32", device="cpu")

# Load and preprocess images from different angles
img1 = preprocess(Image.open("img-1.png")).unsqueeze(0)
img2 = preprocess(Image.open("me.png")).unsqueeze(0)

# Convert to feature embeddings
with torch.no_grad():
    feat1 = model.encode_image(img1)
    feat2 = model.encode_image(img2)

# Compute similarity (cosine similarity)
cos_sim = torch.nn.functional.cosine_similarity(feat1, feat2)
print(f"Similarity Score: {cos_sim.item()}")