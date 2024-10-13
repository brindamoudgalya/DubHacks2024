import cv2
import numpy as np

# Region of Interest function with expanded area
def region_of_interest(img):
    height, width = img.shape
    mask = np.zeros_like(img)
    
    # Adjust the polygon to capture a wider area
    polygon = np.array([[
        (0, height), 
        (width, height), 
        (int(0.6 * width), int(0.6 * height)), 
        (int(0.4 * width), int(0.6 * height))
    ]], np.int32)
    
    cv2.fillPoly(mask, polygon, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

# Process frame function with improved swerve detection
def process_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_frame, 50, 150)
    roi_edges = region_of_interest(edges)
    
    lines = cv2.HoughLinesP(roi_edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    
    left_lane_x = []
    right_lane_x = []
    lane_offset_threshold = 70  # Threshold for swerving detection

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            slope = (y2 - y1) / (x2 - x1 + 0.01)  # Calculate slope, avoid division by zero
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
            
            if slope < 0:  # Left lane
                left_lane_x.append((x1 + x2) // 2)
            elif slope > 0:  # Right lane
                right_lane_x.append((x1 + x2) // 2)

    if left_lane_x and right_lane_x:
        left_lane_position = np.mean(left_lane_x)
        right_lane_position = np.mean(right_lane_x)
        lane_center = (left_lane_position + right_lane_position) / 2

        frame_height, frame_width, _ = frame.shape
        car_position = frame_width / 2  # Assume the car is at the center of the frame

        lane_offset = car_position - lane_center
        if abs(lane_offset) > lane_offset_threshold:
            direction = "left" if lane_offset > 0 else "right"
            cv2.putText(frame, f"Swerving Detected: Moving too far {direction}!", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Centered in Lane", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Optionally, draw lane center line
        cv2.line(frame, (int(lane_center), 0), (int(lane_center), frame_height), (0, 255, 0), 2)
    else:
        # If no lanes detected
        cv2.putText(frame, "No lane lines detected", 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    return frame
