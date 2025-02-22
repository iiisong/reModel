import os
import torch
import clip #For reference: https://openai.com/index/clip/
import threading
from PIL import Image

device = "cpu" #Intel
model, preprocess = clip.load("ViT-B/32", device=device)

FOLDER_PATH = "./couches"  #Edit as needed
BASE_IMAGE_PATH = "base-image.png"

similarity_scores = {}
lock = threading.Lock()

base_image = preprocess(Image.open(BASE_IMAGE_PATH)).unsqueeze(0).to(device)
with torch.no_grad():
    base_feat = model.encode_image(base_image)

#Loop through each img in directory, calculating similarity score for each one
def compute_similarity(image_path):
    try:
        img = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = model.encode_image(img)
        score = torch.nn.functional.cosine_similarity(base_feat, feat).item()
        
        #Thank goodness for threading
        with lock:
            similarity_scores[os.path.basename(image_path)] = score
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def process_images_in_folder():
    threads = []
    image_files = [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH) if f.endswith((".png", ".jpg", ".jpeg"))]

    for image_path in image_files:
        t = threading.Thread(target=compute_similarity, args=(image_path,)) #Turns out you need that comma or Python will take in 17 nonexistent arguments!
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    #Sort our results
    sorted_results = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    print("\nSimilarity Scores:")
    for img, score in sorted_results:
        print(f"{img}: {score:.4f}")

process_images_in_folder()