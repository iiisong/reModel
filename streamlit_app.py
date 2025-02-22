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
import re

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
                results.append({"price": price, "link": href})
                collected_items += 1
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return results

def parse_price(price_str):
    """Parse price and convert to float (handle all formats)"""
    price_str = price_str.replace(",", "")
    match = re.search(r"(\d+(\.\d+)?)", price_str)
    if match:
        return float(match.group(1))
    return 0.0

def get_best_links_within_budget(results, budget, class_names):
    """Select one link per piece of furniture and maximize the budget without exceeding."""
    budget = float(budget)
    
    total_price = 0
    selected_links = []
    
    for i, furniture_results in enumerate(results):
        selected_item = None
        for item in furniture_results:
            price = parse_price(item["price"])
            if total_price + price <= budget:
                selected_item = item
                total_price += price
                break
        
        if selected_item:
            selected_links.append({
                "price": selected_item["price"],
                "link": selected_item["link"],
                "class_name": class_names[i]
            })
    
    return selected_links, total_price

st.title("Decorate Your Room")

budget = st.text_input("Budget", 1000)
style = st.text_input("Style", placeholder="Modern and minimalistic")
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
    results = yolo_model(image)
    
    all_results = []
    class_names = []
    
    for i, result in enumerate(results[0].boxes):
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        cropped_object = image[y1:y2, x1:x2]

        class_id = int(result.cls[0])
        class_name = yolo_model.names[class_id]
        class_names.append(class_name)
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        sam_predictor.set_image(image_rgb)
        input_box = np.array([[x1, y1, x2, y2]])
        masks = sam_predictor.predict(box=input_box)
        
        mask = masks[0].astype(np.uint8) * 255
        masked_object = cv2.bitwise_and(cropped_object, cropped_object, mask=mask[y1:y2, x1:x2])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_path = temp_file.name
            cv2.imwrite(temp_file_path, masked_object)
            st.image(temp_file_path, caption=f"{class_name} {i+1}", width=150)
            
            object_results = reverse_image_search(temp_file_path)
            all_results.append(object_results)
            
            if object_results:
                st.write(f"Similar Products for {class_name} {i+1}:")
                for item in object_results:
                    st.write(item)
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