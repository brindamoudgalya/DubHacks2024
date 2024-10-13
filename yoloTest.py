# alex's test video path: /Users/alexjshepler/Hackathons/DubHacks2024/videos/NoAudio/GRMN0105.MP4

from ultralytics import YOLO
import cv2
from swerveDetection import process_frame

# Load YOLO model
model = YOLO("yolo11n.pt")

# Define a class label mapping for COCO-like dataset (adjust based on your model)
# Modify this list according to your model's specific classes
class_names = {
    0: "Person",
    1: "Bicycle",
    2: "Vehicle",  # General vehicle class, you can distinguish further if the model allows it
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
    # Add more classes if needed based on your model's output
}

# Path to video
video_path = "../NoSwerveDriving.MP4"

# Open video capture
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO object detection
    results = model(frame)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Draw detected objects (YOLO)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Convert tensor label and confidence to Python types
            label_index = int(box.cls)  # Assuming cls is an index
            conf = box.conf.item()  # Convert tensor to float

            # Use the class label mapping to translate index to human-readable label
            label = class_names.get(label_index, f"Unknown({label_index})")

            # Add human-readable object label and confidence
            cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # You can also differentiate between vehicles here, if applicable
            if label == "Vehicle":
                cv2.putText(frame, "Detected: Vehicle", (x1, y2 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # After YOLO detection, apply lane detection and swerving feedback
    frame = process_frame(frame)

    # Display the frame with YOLO and lane detection results
    cv2.imshow('Swerving Detection & YOLO', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
