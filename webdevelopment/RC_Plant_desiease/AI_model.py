import os
import cv2
from ultralytics import YOLO
import shutil

model_path = os.path.join(os.path.dirname(__file__), 'best.pt')
model = YOLO(model_path)

print("[INFO] Model loaded. Classes:", model.names)

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

def process_frame(frame):
    results = model(frame)
    class_name = "No detection"
    conf=0
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            class_name = model.names.get(cls, f'Class {cls}')
            print(f"[DEBUG] Detected {class_name} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")
            label = f'{class_name} {conf:.2f}'

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - h - 5), (x1 + w, y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 0), 2, cv2.LINE_AA)
    return frame, class_name,conf

def process_images_in_directory(input_dir, output_dir):
    clear_directory(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    supported_ext = ['.jpg', '.jpeg', '.png', '.bmp']

    for filename in os.listdir(input_dir):
        if any(filename.lower().endswith(ext) for ext in supported_ext):
            image_path = os.path.join(input_dir, filename)
            frame = cv2.imread(image_path)
            if frame is None:
                print(f"[WARNING] Couldn't read {filename}, skipping.")
                continue

            processed_frame, result, conf = process_frame(frame)
            output_path = os.path.join(output_dir, filename)
            cv2.imwrite(output_path, processed_frame)
            print(f"[INFO] Processed and saved: {output_path}")

def live_processing(frame, output_dir, filename=None):
    os.makedirs(output_dir, exist_ok=True)

    processed_frame, result, conf = process_frame(frame)

    if filename is None:
        import time 
        filename = f"frame_{int(time.time())}.jpg"

    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, processed_frame)
    print(f"[INFO] Live frame processed and saved to: {output_path}")

    return processed_frame, result, conf
   


if __name__ == '__main__':
    process_images_in_directory('./input', './static/predictions')
