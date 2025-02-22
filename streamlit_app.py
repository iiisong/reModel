import streamlit as st
import cv2
import torch
import numpy as np
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import tempfile
import os

yolo_model = YOLO("yolov8m.pt")

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam_predictor = SamPredictor(sam)

def reverse_image_search(image_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    results = []
    
    try:
        driver.get("https://images.google.com/")

        lens_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Gdd5U"))
        )
        lens_button.click()

        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        upload_input.send_keys(image_path)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        time.sleep(3)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        collected_items = 0
        spans = soup.find_all("span", class_="EwVMFc")
        
        for span in spans:
            if collected_items >= 5:
                break
            
            next_link = span.find_next("a", href=True)
            if next_link and next_link["href"].startswith("http"):
                price = span.get_text(strip=True)[:-1]
                href = next_link["href"]
                results.append(f"Price: {price} - Link: {href}")
                collected_items += 1
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return results

st.title("Decorate Your Room")

title = st.text_input("Budget", placeholder="$1000")

title = st.text_input("Style", placeholder="Modern and minimalistic")

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
    results = yolo_model(image)
    
    for i, result in enumerate(results[0].boxes):
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        cropped_object = image[y1:y2, x1:x2]
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        sam_predictor.set_image(image_rgb)
        input_box = np.array([[x1, y1, x2, y2]])
        masks = sam_predictor.predict(box=input_box)
        
        mask = masks[0].astype(np.uint8) * 255
        masked_object = cv2.bitwise_and(cropped_object, cropped_object, mask=mask[y1:y2, x1:x2])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            cv2.imwrite(temp_file_path, masked_object)
            st.image(temp_file_path, caption=f"Furniture {i+1}", width=150)
            
            object_results = reverse_image_search(temp_file_path)
            
            if object_results:
                st.write("Similar Products:")
                for item in object_results:
                    st.write(item)
            else:
                st.write("No relevant items found.")
            
            os.remove(temp_file_path)