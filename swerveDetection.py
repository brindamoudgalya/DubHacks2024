import cv2
import numpy as np

def region_of_interest(img):
    height, width = img.shape
    mask = np.zeros_like(img)
    
    polygon = np.array([[(0, height), (width, height), (width // 2, height // 2)]])
    cv2.fillPoly(mask, polygon, 255)
    
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def process_frame(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray_frame, 50, 150)
    roi_edges = region_of_interest(edges)
    
    lines = cv2.HoughLinesP(roi_edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    
    left_lane_x = []
    right_lane_x = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
            if x1 < frame.shape[1] // 2:
                left_lane_x.append(x1)
            else:
                right_lane_x.append(x1)

    if left_lane_x and right_lane_x:
        left_lane_position = np.mean(left_lane_x)
        right_lane_position = np.mean(right_lane_x)

        lane_center = (left_lane_position + right_lane_position) / 2
        frame_height, frame_width, _ = frame.shape
        car_position = frame_width / 2  # Assume the car is positioned at the center of the frame
        
        # Check for swerving and add human-readable feedback
        if car_position < left_lane_position:
            cv2.putText(frame, "Swerving Detected: Moving too far left!", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif car_position > right_lane_position:
            cv2.putText(frame, "Swerving Detected: Moving too far right!", 
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
