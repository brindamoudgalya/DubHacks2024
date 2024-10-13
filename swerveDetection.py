import cv2
import numpy as np

def region_of_interest(img):
    height, width = img.shape
    mask = np.zeros_like(img)
    
    # Define the polygon for the region of interest (the lower half of the frame)
    polygon = np.array([[(0, height), (width, height), (width // 2, height // 2)]])
    
    # Fill the polygon with white to create the mask
    cv2.fillPoly(mask, polygon, 255)
    
    # Apply the mask to the image
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Preprocess frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_frame, 50, 150)
        roi_edges = region_of_interest(edges)
        
        # Detect lanes
        lines = cv2.HoughLinesP(roi_edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
        
        # Prepare to store lane positions
        left_lane_x = []
        right_lane_x = []

        # Draw lines and analyze lane position
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                # Store x positions of detected lanes
                if x1 < frame.shape[1] // 2:  # Left lane
                    left_lane_x.append(x1)
                else:  # Right lane
                    right_lane_x.append(x1)

        # Analyze lane positions if we have detected lanes
        if left_lane_x and right_lane_x:
            # Average positions of detected lane lines
            left_lane_position = np.mean(left_lane_x)
            right_lane_position = np.mean(right_lane_x)

            # Calculate the center of the lane
            lane_center = (left_lane_position + right_lane_position) / 2

            # Assume the car is in the middle of the frame horizontally
            # For simplicity, let's assume the car is positioned at the center of the bottom half of the frame
            frame_height, frame_width, _ = frame.shape
            car_position = frame_width / 2  # Center of the frame

            # Check if the car is swerving
            if car_position < left_lane_position or car_position > right_lane_position:
                # The vehicle is swerving
                cv2.putText(frame, "Swerving Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Optionally, draw lane center line
            cv2.line(frame, (int(lane_center), 0), (int(lane_center), frame_height), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Lane Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Call the function with the path to your video file
process_video('path/to/video.mp4')
