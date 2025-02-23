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
from urllib.parse import urlparse

st.set_page_config(layout="wide")

from src.products_parse import get_best_links_within_budget
from src.product_search import product_search
from src.stabledesign import stabledesign
from src.product_search import product_search
from src.stabledesign import stabledesign

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
    
    container = st.container()

    with container:
        col1, col2 = st.columns([1, 2])

        image = Image.open(uploaded_file)
        image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
        image.save(image_path)
        
        with col1:
            st.image(image, caption="Before", width=400)
        
        gen_image = stabledesign(image, prompt, optimize=True)
        
        with col1:
            st.image(gen_image, caption="After", width=400)

        final_image = np.array(gen_image)
        final_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)

        results = yolo_model(final_image)
        
        all_results = []
        class_names = []
        
        pri = []
        last = []
        for obj in results[0].boxes:
            if 'plant' in (yolo_model.names[int(obj.cls[0])]):
                last.append(obj)
            else:
                pri.append(obj)
        objects = pri + last

        with col2: 
            for i, result in enumerate(objects):
                x1, y1, x2, y2 = map(int, result.xyxy[0])
                cropped_object = final_image[y1:y2, x1:x2]

                class_id = int(result.cls[0])
                class_name = yolo_model.names[class_id].capitalize()
                class_names.append(class_name)
                
                image_rgb = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR) 
                sam_predictor.set_image(image_rgb)
                input_box = np.array([[x1, y1, x2, y2]])
                masks = sam_predictor.predict(box=input_box)
                
                mask = masks[0].astype(np.uint8) * 255
                masked_object = cv2.bitwise_and(cropped_object, cropped_object, mask=mask[y1:y2, x1:x2])

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file_path = temp_file.name
                    cv2.imwrite(temp_file_path, masked_object)
                    
                    object_results = product_search(temp_file_path)
                    all_results.append(object_results)
                    
                    with st.expander(f"{class_name}"):
                        minicontainer = st.container()
                        with minicontainer:
                            minicol1, minicol2 = st.columns([1, 1])
                            minicol1.image(temp_file_path, width=150)
                            minicol2.markdown(f"<span style='font-weight: bold; text-transform: uppercase; font-size: 32px;'>{class_name}</span>", unsafe_allow_html=True)
                        if object_results:
                            for i, item in enumerate(object_results):
                                 domain = urlparse(item['link']).netloc.split('.')[-2].capitalize()
                                 st.markdown(f"""
                                    <div style="border: 2px solid #000; padding: 10px; margin-bottom: 10px; border-color: white; display: flex; align-items: center;">
                                        <img src="{item['img']}" width="150" style="margin-right: 20px;" />
                                        <div>
                                            <p style="font-weight: bold;"><a href="{item['link']}">Product {i+1}</a></p>
                                            <p><strong>Price:</strong> {item['price']}</p>
                                            <p><strong>Domain:</strong> {domain}</p>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.write("No relevant items found.")
                    os.remove(temp_file_path)
    
        if all_results:
            st.markdown("## Optimal Budgeted Products:")
            selected, total_price, class_matches = get_best_links_within_budget(all_results, budget, class_names)
            
            if selected:
                st.write(f"Total Price: ${total_price:.2f}")
                for itr, item in enumerate(selected):
                    domain = urlparse(item['link']).netloc.split('.')[-2].capitalize()
                    st.markdown(f"""
                        <div style="border: 2px solid #000; padding: 10px; margin-bottom: 10px; border-color: white; display: flex; flex-direction: column; align-items: flex-start;">
                            <div style="font-weight: bold; font-size: 18px; margin-bottom: 10px;">{class_matches[itr]}</div>
                            <div style="display: flex; align-items: center;">
                                <img src="{item['img']}" width="150" style="margin-right: 20px;" />
                                <div>
                                    <p style="font-weight: bold;"><a href="{item['link']}">Product {itr+1}</a></p>
                                    <p><strong>Price:</strong> {item['price']}</p>
                                    <p><strong>Domain:</strong> {domain}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            else:
                st.write("No items fit within the budget.")
        else:
            st.write("No relevant items found.")