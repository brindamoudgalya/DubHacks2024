import pyrealsense2 as rs
import numpy as np
import cv2
import dlib

# Initialize dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def detect_fatigue(landmarks):
    """Detect if the user is yawning or looking down."""
    mouth = landmarks[61:68]
    left_eye = landmarks[36:42]
    right_eye = landmarks[42:48]

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

                yawn, look_down = detect_fatigue(landmarks_np)
                status = "Yawning" if yawn else "Looking Down" if look_down else "Alert"

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
    cv2.destroyAllWindows()
    print("Camera pipeline stopped.")
