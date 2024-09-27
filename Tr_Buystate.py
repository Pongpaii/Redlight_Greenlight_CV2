import cv2
import numpy as np
import time

# ฟังก์ชันแสดงข้อความการซื้อของ
def show_buy_item_menu(frame):
    display_text(frame, "Press 'S' to buy Speed Potion (10 Coins)", (300, 360), 1.5, (255, 255, 255), 2)
    display_text(frame, "Press 'T' to skip", (300, 420), 1.5, (255, 255, 255), 2)
    display_text(frame, f"Total Coins: {coins}", (50, 50), 1, (255, 255, 255), 2)

# เพิ่มไอเทมน้ำยาเพิ่มความเร็ว
speed_potion_active = False  # สถานะน้ำยาเพิ่มความเร็ว
speed_potion_duration = 10  # น้ำยาเพิ่มความเร็วจะทำงานเป็นเวลา 10 วินาที
speed_potion_end_time = 0  # เวลาที่น้ำยาหมดอายุ

def countdown_to_main_menu(frame, countdown_seconds=2):
    for i in range(countdown_seconds, 0, -1):
        frame_copy = frame.copy()  # สร้างสำเนาของเฟรม
        display_text(frame_copy, f"Returning to main menu in {i} seconds...", (250, 500), 2, (255, 255, 255), 3)
        cv2.imshow(window_name, frame_copy)
        cv2.waitKey(1000)  # รอ 1 วินาทีต่อแต่ละการนับถอยหลัง

# Initial settings
window_name = "Redlight Greenlight Game"
width, height = 1280, 720
bg_image = cv2.imread('Resources/Menu/Bg.jpeg')
bg_image = cv2.resize(bg_image, (width, height))  # ปรับขนาดภาพพื้นหลัง

# ปุ่มสำหรับเลือกตัวละคร
player_button_images = ['Resources/Menu/player1.png', 'Resources/Menu/player2.png', 'Resources/Menu/player3.png']

# ตัวละครต่าง ๆ
character1 = cv2.imread('Resources/Menu/1Char.png', cv2.IMREAD_UNCHANGED)
character2 = cv2.imread('Resources/Menu/Kai_Onstove.png', cv2.IMREAD_UNCHANGED)
character3 = cv2.imread('Resources/Menu/Bada_Onstove.png', cv2.IMREAD_UNCHANGED)
background_selection_screen = cv2.imread('Resources/Menu/Choose.jpg')
background_selection_screen = cv2.resize(background_selection_screen, (width, height))

# ตั้งค่าเริ่มต้น
character = None
character_size = 0.1  # Initial size of the character
max_size = 600 / character1.shape[0]  # Maximum size
game_time = 120  # 2 minutes in seconds
game_state = "Greenlight"  # Initial state
game_over = False
win = False  # Track win state
timer_started = False
start_time = None
game_started = False
character_selected = False  # เช็คว่าผู้เล่นได้เลือกตัวละครหรือยัง

# Coin system
coins = 0  # Initialize total coins

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ไม่สามารถเปิดกล้องได้")
    exit()

# ฟังก์ชันสำหรับแสดงข้อความบนภาพ
def display_text(frame, text, position, font_scale=1, color=(255, 255, 255), thickness=2):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

# ฟังก์ชันตรวจจับการเคลื่อนไหว
def check_movement(prev_frame, current_frame, threshold=25):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, current_gray)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    movement = np.sum(thresh) / 255
    return movement > 5000  # ค่าขีดจำกัดว่ามีการเคลื่อนไหวหรือไม่

# อ่านเฟรมแรกจากกล้อง
ret, prev_frame = cap.read()
if not ret:
    print("ไม่สามารถอ่านเฟรมจากกล้องได้")
    cap.release()
    exit()

# Main game loop
while True:
    ret, current_frame = cap.read()
    if not ret:
        print("ไม่สามารถอ่านเฟรมจากกล้องได้")
        break

    frame = bg_image.copy()

    # ถ้ายังไม่เลือกตัวละคร แสดงปุ่มเลือกตัวละคร
    if not character_selected:
        frame = background_selection_screen.copy()
        display_text(frame, f"Total Coins: {coins}", (50, 50), 1, (255, 255, 255), 2)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('1'):
            character = character1
            character_selected = True
            game_state = "BuyItem"
        elif key == ord('2'):
            character = character2
            character_selected = True
            game_state = "BuyItem"
        elif key == ord('3'):
            character = character3
            character_selected = True
            game_state = "BuyItem"
        continue

    # ถ้าอยู่ใน state การซื้อไอเทม
    if game_state == "BuyItem":
        show_buy_item_menu(frame)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('s'):  # กด 'S' เพื่อซื้อน้ำยาเพิ่มความเร็ว
            if coins >= 10:
                coins -= 10
                speed_potion_active = True
                speed_potion_end_time = time.time() + speed_potion_duration
                game_state = "ReadyToPlay"
            else:
                display_text(frame, "Not enough coins!", (300, 480), 1.5, (0, 0, 255), 2)
        elif key == ord('t'):  # กด 'T' เพื่อข้ามการซื้อ
            game_state = "ReadyToPlay"
        continue

    # ถ้ายังไม่เริ่มเกม
    if game_state == "ReadyToPlay":
        # ปรับขนาด character ที่เลือก
        character_resized = cv2.resize(character, (0, 0), fx=character_size, fy=character_size)
        display_text(frame, "Are you ready? Press 'P' to start", (300, 360), 2, (255, 255, 255), 3)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('p'):  # กด 'P' เพื่อเริ่มเกม
            game_started = True
            start_time = time.time()
            game_state = "Greenlight"
        continue

    # ตรวจจับการเคลื่อนไหว
    movement_detected = check_movement(prev_frame, current_frame)

    # ตรวจสอบการใช้น้ำยาเพิ่มความเร็ว
    if speed_potion_active:
        if time.time() > speed_potion_end_time:
            speed_potion_active = False
        else:
            character_size = min(character_size + 0.05, max_size)
    else:
        if movement_detected and game_state == "Greenlight":
            character_size = min(character_size + 0.02, max_size)

    # อัพเดทเฟรมก่อนหน้า
    prev_frame = current_frame.copy()

    # ตรวจสอบว่าตัวละครมีช่องสี 4 ช่อง (RGBA) หรือไม่
    if character_resized.shape[2] == 4:
        # แปลง RGBA เป็น RGB โดยลบช่อง Alpha
        character_resized = cv2.cvtColor(character_resized, cv2.COLOR_BGRA2BGR)

    # วาง character ลงบน frame
    frame[height - character_resized.shape[0]: height,
    width // 2 - character_resized.shape[1] // 2: width // 2 + character_resized.shape[1] // 2] = character_resized

    # ตรวจสอบเวลาหมด
    elapsed_time = int(time.time() - start_time)
    time_left = max(0, game_time - elapsed_time)
    if time_left == 0:
        game_over = True

    # แสดงเวลาที่เหลือ
    display_text(frame, f"Time left: {time_left} seconds", (50, 50), 1.5, (255, 255, 255), 2)

    # แสดงข้อความจบเกม
    if game_over:
        display_text(frame, "Game Over!", (500, 500), 3, (0, 0, 255), 5)
        countdown_to_main_menu(frame)
        game_over = False
        character_selected = False  # รีเซ็ตการเลือกตัวละครเพื่อเริ่มเกมใหม่

    # แสดงเฟรม
    cv2.imshow(window_name, frame)

    # ออกเกมด้วยการกดปุ่ม 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปล่อยกล้อง
cap.release()
# ปิดหน้าต่างทั้งหมด
cv2.destroyAllWindows()
