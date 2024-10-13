from ultralytics import YOLO
import cv2
import csv
from datetime import datetime, timedelta
from swerveDetection import process_frame
import os

# Load YOLO model
model = YOLO("yolo11n.pt")

# Define a class label mapping for COCO-like dataset (adjust based on your model)
class_names = {
    0: "Person",
    1: "Bicycle",
    2: "Vehicle",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck",
}

# Path to video
video_path = "../TestDrivingVideo.MP4"

# Open video capture
cap = cv2.VideoCapture(video_path)

# Variables to track swerving
swerving_count = 0
previous_lane_centers = []

# Open CSV file to append data
csv_file = "swerve_detection_results.csv"

# Function to read the last date from the CSV
def get_last_csv_date():
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            last_row = list(reader)[-1]  # Get the last row
            last_date_str = last_row[0]
            last_date = datetime.strptime(last_date_str, "%m/%d/%Y")
            return last_date
    return None

# Function to increment the last date by 1 day
def get_next_date(last_date):
    return last_date + timedelta(days=1)

# Function to update the CSV by appending the new date and swerving count
def update_csv(date, speeding, swerving):
    # Read the last date and increment it
    data = []
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            data = list(reader)

    # Append new data (with incremented date)
    data.append([date.strftime("%m/%d/%Y"), speeding, swerving])

    # Write the updated data back to the CSV
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Function to detect swerving in process_frame and increment swerving count
def detect_swerving(frame):
    global swerving_count
    processed_frame, swerving_detected = process_frame(frame)

    # Increment swerving count based on detection
    if swerving_detected:
        swerving_count += 1

    return processed_frame

# Get the last date from the CSV and increment it
last_date = get_last_csv_date()
if last_date is None:
    last_date = datetime.now()  # Default if no previous date is found

next_date = get_next_date(last_date)

# Track if speeding occurred (for now, set to 0 each time)
speeding = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO object detection
    results = model(frame)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            label_index = int(box.cls)
            conf = box.conf.item()
            label = class_names.get(label_index, f"Unknown({label_index})")
            cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if label == "Vehicle":
                cv2.putText(frame, "Detected: Vehicle", (x1, y2 + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Detect swerving in the frame
    processed_frame = detect_swerving(frame)

    # Display the frame with YOLO and lane detection results
    cv2.imshow('Swerving Detection & YOLO', processed_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture
cap.release()
cv2.destroyAllWindows()

# Update the CSV with the incremented date and swerving count
update_csv(next_date, speeding, swerving_count)
