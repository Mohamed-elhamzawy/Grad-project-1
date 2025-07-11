import time
import cv2
import os
import requests
from RC_Plant_desiease.AI_model import live_processing
import shutil

ESP_URL = "http://192.168.8.50/action" # Change this if your ESP IP is different
STREAM_URL = "http://192.168.8.40:5000/video_feed"  # Endpoint that returns an image frame (you must have this on ESP)
INPUT_DIR = './input'
PRED_DIR = './static/predictions'

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(PRED_DIR, exist_ok=True)

def send_command_to_esp(command):
    try:
        # url = f"{ESP_URL}/action?cmd={command}"
        # print("debug: Sending command to ESP:", url)
        response = requests.post(f"{ESP_URL}/{command}")
        #Example command: /action?cmd=move");
        # response = requests.post(ESP_URL, data={"cmd": "{command}"}) 
        print(f"[INFO] Sent command '{command}' → Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send '{command}' to ESP: {e}")

def clear_directory(dir_path):
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # remove subdirectory
            except Exception as e:
                print(f"[ERROR] Failed to delete {file_path}: {e}")

def capture_image():

    try:
        cap = cv2.VideoCapture(STREAM_URL)

        if not cap.isOpened():
            print("[ERROR] Could not open stream.")
            return None

        # Read one frame
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            print("[ERROR] Failed to read frame from stream.")
            return None

        # Save image to disk
        timestamp = int(time.time())
        image_path = os.path.join(INPUT_DIR, f'current_{timestamp}.jpg')
        cv2.imwrite(image_path, frame)
        print(f"[INFO] Image captured: {image_path}")

        return frame

    except Exception as e:
        print(f"[ERROR] Error while capturing image from stream: {e}")
        return None

def is_plant_healthy(image):
    processed_frame, class_name, conf = live_processing(image,PRED_DIR, filename=f'prediction_{int(time.time())}.jpg')
    output_path = os.path.join(PRED_DIR, f'prediction_{int(time.time())}.jpg')
    cv2.imwrite(output_path, processed_frame)
    print(f"[INFO] Classification result: {class_name}")
    if conf > 0.2 and class_name.lower() not in ["healthy", "no detection"]:
        print("[WARNING] Low confidence in classification, assuming plant is healthy.")
        return True
    if  class_name.lower() == "healthy" or class_name.lower() == "no detection":
        print("[INFO] Plant is healthy.")
        return True


def run_cycle():
    print("[INFO] Starting automatic plant check cycle...")
    print("[INFO] Clearing previous input and prediction files...")
    clear_directory(INPUT_DIR)
    clear_directory(PRED_DIR)
    l=8
    for stop_num in range(l):
        print(f"\n[INFO] --- Stop {stop_num+1}/{l} ---")

        send_command_to_esp("stop")
        time.sleep(1)  # Let the car settle

        image = capture_image()
        if image is None:
            print("[WARNING] Skipping due to image capture failure.")
            send_command_to_esp("move")
            time.sleep(4)
            continue

        if is_plant_healthy(image):
            print("[INFO] Plant is healthy. Moving forward.")
            send_command_to_esp("move")
            time.sleep(4)
        else:
            print("[INFO] Plant is diseased. Spraying...")
            send_command_to_esp("spray")
            time.sleep(4)
            send_command_to_esp("move")
            time.sleep(4)

    send_command_to_esp("stop")
    print("[INFO] Cycle completed. Car stopped.")

if __name__ == "__main__":
    run_cycle()
