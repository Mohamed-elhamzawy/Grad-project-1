import cv2
import requests
import numpy as np
import time

# MJPEG stream URL
url = "http://192.168.1.15:5000/video_feed"

# Connect to the stream
stream = requests.get(url, stream=True)
if stream.status_code != 200:
    print("❌ Failed to connect to video stream")
    exit()

print("📷 Press 'b' to capture an image, 'q' to quit")

bytes_buffer = b""
img_count = 0

for chunk in stream.iter_content(chunk_size=1024):
    bytes_buffer += chunk
    a = bytes_buffer.find(b'\xff\xd8')
    b = bytes_buffer.find(b'\xff\xd9')

    if a != -1 and b != -1:
        jpg = bytes_buffer[a:b+2]
        bytes_buffer = bytes_buffer[b+2:]

        img_np = np.frombuffer(jpg, dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if frame is not None:
            cv2.imshow("Live Stream", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('b'):
                filename = f"snapshot_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"✅ Saved snapshot as {filename}")
            elif key == ord('q'):
                print("👋 Exiting...")
                break

cv2.destroyAllWindows()
