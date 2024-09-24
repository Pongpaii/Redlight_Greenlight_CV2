import cvzone
from cvzone.HandTrackingModule import HandDetector
import cv2
import numpy as np
import subprocess
import time
import mediapipe

def get_finger_location(img, imgWarped):
    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand1 = hands[0]
        finger_point = hand1["lmList"][8][0:2]
        cv2.circle(imgWarped, finger_point, 5, (255, 0, 0), cv2.FILLED)
    else:
        finger_point = None
    return finger_point, hands  # คืนค่าทั้งตำแหน่งนิ้วและข้อมูลของมือ

# Setting camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
hf = 720
wf = 1280
cap.set(3, wf)
cap.set(4, hf)

detector = HandDetector(staticMode=False,
                        maxHands=1,
                        modelComplexity=1,
                        detectionCon=0.5,
                        minTrackCon=0.5)

# Read and resize background
BGimg_org = cv2.imread("Resources/Menu/Play_page1.png")
BGimg_org = cv2.resize(BGimg_org, (wf, hf))

# Load Play button image
play_button_img = cv2.imread("Resources/Menu/Play_button.png")
play_button_img = cv2.resize(play_button_img, (200, 100))  # Resize button to desired size

# Define the button's position
play_button_x = 50  # x-coordinate of the button
play_button_y = (hf - 100) // 2  # Center vertically on the left side

# Initialize timer
hover_start_time = None

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Show the background
    imgWarped = BGimg_org.copy()
    imgWarped[play_button_y:play_button_y + 100, play_button_x:play_button_x + 200] = play_button_img  # Draw button

    finger_point, hands = get_finger_location(img, imgWarped)  # รับค่าจากฟังก์ชัน

    if finger_point:
        print(f"Finger Point: {finger_point}")  # Debugging
        if (play_button_x < finger_point[0] < play_button_x + 200 and
                play_button_y < finger_point[1] < play_button_y + 100):
            # Check if the finger is over the button
            cv2.rectangle(imgWarped, (play_button_x, play_button_y),
                          (play_button_x + 200, play_button_y + 100),
                          (0, 255, 0), 2)  # Draw rectangle around button

            if hands and detector.fingersUp(hands[0])[0] == 1:  # Check if the index finger is up
                print("Finger is up")  # Debugging
                if hover_start_time is None:
                    hover_start_time = time.time()  # Start timer
                elif time.time() - hover_start_time >= 3:  # Check if hovered for 3 seconds
                    print("Starting redlightgreen.py")  # Debugging
                    subprocess.run(["python", "redlightgreen.py"])  # Open redlightgreen.py
            else:
                hover_start_time = None  # Reset timer if finger is not up
        else:
            hover_start_time = None  # Reset timer if finger is not over the button

    # Display the image
    cv2.imshow("Menu Game", imgWarped)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
