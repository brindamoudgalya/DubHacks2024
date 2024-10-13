import pyrealsense2 as rs
import numpy as np
import cv2
import dlib
import serial
import time

# Initialize dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Replace 'COM3' with your Arduino's correct port (e.g., 'COM4' on Windows or '/dev/ttyUSB0' on Linux/Mac)
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Allow time for the serial connection to initialize
    print("Connected to Arduino")
except serial.SerialException as e:
    print(f"Error: Could not connect to Arduino - {e}")
    exit()

def detect_fatigue(landmarks):
    """Detect if the user is yawning or looking down."""
    mouth = landmarks[48:60]
    left_eye = landmarks[36:42]
    right_eye = landmarks[42:48]

    # Calculate mouth and eye metrics for yawning and looking down detection
    mouth_height = np.linalg.norm(mouth[3] - mouth[9])
    mouth_width = np.linalg.norm(mouth[0] - mouth[6])
    yawn_ratio = mouth_height / mouth_width

    eye_height = np.mean([
        np.linalg.norm(left_eye[1] - left_eye[5]),
        np.linalg.norm(right_eye[1] - right_eye[5])
    ])
    eye_width = np.mean([
        np.linalg.norm(left_eye[0] - left_eye[3]),
        np.linalg.norm(right_eye[0] - right_eye[3])
    ])
    gaze_ratio = eye_height / eye_width

    is_yawning = yawn_ratio > 0.6
    is_looking_down = gaze_ratio < 0.2

    return is_yawning, is_looking_down

def send_down(looking_down):
    try:
        signal = '2' if looking_down else '0'
        arduino.write(signal.encode())
        print(f"Sent signal: {signal}")
    except serial.SerialException as e:
        print(f"Error sending signal: {e}")

def send_yawn(is_yawning):
    """Send '1' to Arduino if yawning, '0' otherwise."""
    try:
        signal = '1' if is_yawning else '0'
        arduino.write(signal.encode())
        print(f"Sent signal: {signal}")
    except serial.SerialException as e:
        print(f"Error sending signal: {e}")

# Set up RealSense camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

try:
    pipeline.start(config)
    print("RealSense pipeline started. Waiting for frames...")

    while True:
        try:
            frames = pipeline.wait_for_frames(timeout_ms=5000)
            color_frame = frames.get_color_frame()

            if not color_frame:
                print("No frame received.")
                continue

            frame = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)
                landmarks_np = np.array([[p.x, p.y] for p in landmarks.parts()])

                # Detect yawning and send signal to Arduino
                yawn, look_down = detect_fatigue(landmarks_np)
                send_yawn(yawn)
                send_down(look_down)

                # Display bounding box and yawning status on screen
                status = "Yawning" if yawn else "Sleeping or looking down" if look_down else "Alert"
                cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
                cv2.putText(frame, status, (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.imshow("Driver Fatigue Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except RuntimeError as e:
            print(f"Error: {e}")
            break

finally:
    pipeline.stop()
    arduino.close()
    cv2.destroyAllWindows()
    print("Camera pipeline and Arduino connection closed.")
