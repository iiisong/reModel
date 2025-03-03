from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor
import cv2
import numpy as np

yolo_model = YOLO("yolov8m.pt")

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam_predictor = SamPredictor(sam)

def object_detect(img):
    masked_images = []
    results = yolo_model(img)
    
    for i, result in enumerate(results[0].boxes):
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        cropped_object = img[y1:y2, x1:x2]

        sam_predictor.set_image(img)
        input_box = np.array([[x1, y1, x2, y2]])
        masks = sam_predictor.predict(box=input_box)
        
        mask = masks[0].astype(np.uint8) * 255
        masked_object = cv2.bitwise_and(cropped_object, cropped_object, mask=mask[y1:y2, x1:x2])
        
        masked_images.append(masked_object)
    
    return masked_images