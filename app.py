import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor
import tempfile
import os
from PIL import Image
import replicate
import dotenv

from src.stabledesign import stabledesign
from src.products_parse import get_best_links_within_budget
from src.reverse_img_search import reverse_image_search
from src.stbdes_openai import query_redesign

dotenv.load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    st.error("Missing Replicate API token. Please check your .env file.")
else:
    replicate.client = replicate.Client(api_token=REPLICATE_API_TOKEN)


yolo_model = YOLO("yolov8m.pt")

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam_predictor = SamPredictor(sam)



st.title("Decorate Your Room")

INTRO = """
*Developed by Anthony Zang, Chandreyi (Zini) Chakraborty, Isaac Song, Kieran Slattery*

*Hacklytics 2025 @ Georgia Tech*


"""

st.write(INTRO)
    
budget = st.text_input("Budget", 1000)
prompt = st.text_input("Style", placeholder="Modern and minimalistic")
uploaded_file = st.file_uploader("Choose a room...", type=["jpg", "jpeg", "png"])


if st.button('Reimagine Your Room') and uploaded_file:
    st.write('### Reimagining your room...')
    
    image = Image.open(uploaded_file)
    image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
    image.save(image_path)
    
    st.image(image, caption="Before", use_container_width=True)
    
    gen_image = query_redesign(image, prompt)
    
    st.image(gen_image, caption="After", use_container_width=True)

    final_image = np.array(gen_image)
    final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)

    results = yolo_model(final_image)
    
    all_results = []
    class_names = []
    
    for i, result in enumerate(results[0].boxes):
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        cropped_object = final_image[y1:y2, x1:x2]

        class_id = int(result.cls[0])
        class_name = yolo_model.names[class_id]
        class_names.append(class_name)
        
        image_rgb = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR) 
        sam_predictor.set_image(image_rgb)
        input_box = np.array([[x1, y1, x2, y2]])
        masks = sam_predictor.predict(box=input_box)
        
        mask = masks[0].astype(np.uint8) * 255
        masked_object = cv2.bitwise_and(cropped_object, cropped_object, mask=mask[y1:y2, x1:x2])
        
        st.markdown(f"## {class_name}")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            cv2.imwrite(temp_file_path, masked_object)
            st.image(temp_file_path, width=150)
            
            object_results = reverse_image_search(temp_file_path)
            all_results.append(object_results)
            
            if object_results:
                st.write(f"Similar Products for {class_name}:")
                for item in object_results:
                    st.write(f"Price: {item['price']}")
                    st.write(f"Link: {item['link']}")
                    st.image(item['img'], width=150)
            else:
                st.write("No relevant items found.")
            
            os.remove(temp_file_path)
    
    if all_results:
        st.markdown("# Optimal Budgeted Products:")
        selected_links, total_price = get_best_links_within_budget(all_results, budget, class_names)
        
        if selected_links:
            st.write(f"Total Price: ${total_price:.2f}")
            for item in selected_links:
                st.markdown(f"## {item['class_name']}")
                st.write(f"Price: {item['price']}")
                st.write(f"Link: {item['link']}")

        else:
            st.write("No items fit within the budget.")
    else:
        st.write("No relevant items found.")