import cv2
import numpy as np
import pyautogui

# Initialize webcam
cap = cv2.VideoCapture(0)

# Set up mouse control parameters
screen_width, screen_height = pyautogui.size()
mouse_speed = 10

# Initialize finger count for volume control
finger_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for natural hand movement
    frame = cv2.flip(frame, 1)

    # Convert the frame from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range of skin color in HSV
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Extract skin color
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Remove noise using morphological operations
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Find contours of the hand region
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour (hand)
        hand_contour = max(contours, key=cv2.contourArea)

        # Find the convex hull
        hull = cv2.convexHull(hand_contour)

        # Draw the convex hull (skeleton) in green
        cv2.drawContours(frame, [hull], -1, (0, 255, 0), 2)

        # Find the centroid of the hand
        M = cv2.moments(hand_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Move the mouse based on hand position
            x = int((cx / frame.shape[1]) * screen_width)
            y = int((cy / frame.shape[0]) * screen_height)
            pyautogui.moveTo(x, y, duration=0)

            # Detect number of fingers (volume control)
            hull = cv2.convexHull(hand_contour, returnPoints=False)
            if len(hull) > 3:
                defects = cv2.convexityDefects(hand_contour, hull)
                if defects is not None:
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        start = tuple(hand_contour[s][0])
                        end = tuple(hand_contour[e][0])
                        far = tuple(hand_contour[f][0])
                        if d > 10000:  # Tune this threshold as needed
                            finger_count += 1
                            cv2.circle(frame, far, 5, [0, 0, 255], -1)

            # Perform actions based on finger count
            if finger_count == 2:
                pyautogui.hotkey('command', 'up')  # Increase volume on Mac, adjust as needed
            elif finger_count == 1:
                pyautogui.click()  # Left-click
            elif finger_count == 3:
                pyautogui.rightClick()  # Right-click
            elif finger_count == 4:
                pyautogui.hotkey('command', 'o')  # Open file dialog on Mac, adjust as needed

    # Display the frame
    cv2.imshow('Virtual Mouse', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
