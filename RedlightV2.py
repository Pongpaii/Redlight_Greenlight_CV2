import cv2
import numpy as np
import pygame
import time

# กำหนดค่าต่างๆ
cap = cv2.VideoCapture(0)  # ใช้กล้องเว็บแคม
width, height = int(cap.get(3)), int(cap.get(4))

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Load sound files
greenlight_sound = pygame.mixer.Sound("greenLight.mp3")
redlight_sound = pygame.mixer.Sound("redLight.mp3")

# ฟังก์ชันตรวจจับการเคลื่อนไหว
def detect_movement(prev_frame, curr_frame):
    # คำนวณค่า difference และ threshold
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # ตรวจสอบว่ามีการเคลื่อนไหวหรือไม่
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            return True
    return False

# ฟังก์ชันแสดงข้อความบนหน้าจอ
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

# เริ่มเกม
prev_frame = None
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    # ตรวจจับการเคลื่อนไหว
    if prev_frame is None:
        prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # แปลงเป็น grayscale สำหรับเฟรมแรก
        continue

    # เล่นเสียง greenlight และสุ่มเวลา
    greenlight_sound.play()
    draw_text(frame, "RUN!", width // 2 - 100, height // 2)
    cv2.imshow("Red Light Green Light", frame)
    cv2.waitKey(np.random.randint(3000, 5000))  # รอ 3-5 วินาที

    # เล่นเสียง redlight และตรวจจับการเคลื่อนไหว
    redlight_sound.play()
    draw_text(frame, "STOP!", width // 2 - 100, height // 2)
    cv2.imshow("Red Light Green Light", frame)
    if detect_movement(prev_frame, frame):
        draw_text(frame, "You're dead!", width // 2 - 150, height // 2 + 50)
        cv2.imshow("Red Light Green Light", frame)
        cv2.waitKey(3000)
        break

    prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # เก็บเฟรมปัจจุบันเป็น grayscale สำหรับการเปรียบเทียบครั้งถัดไป
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
