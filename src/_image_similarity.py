import torch
import clip
from PIL import Image
import streamlit as st

def image_similarity(img1, img2):
    model, preprocess = clip.load("ViT-B/32", device="cpu")

    img1 = preprocess(Image.open(img1)).unsqueeze(0)
    img2 = preprocess(Image.open(img2)).unsqueeze(0)

    with torch.no_grad():
        feat1 = model.encode_image(img1)
        feat2 = model.encode_image(img2)

    cos_sim = torch.nn.functional.cosine_similarity(feat1, feat2)
    if (cos_sim.item() > .85):
        st.write("Repeat Image")
    else:
        st.write(cos_sim.item())
    return (cos_sim.item() > .85)