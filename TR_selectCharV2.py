import cv2
import numpy as np
import time

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


# ตั้งค่าเริ่มต้น
character = None
character_size = 0.1  # Initial size of the character (very small)
max_size = 600 / character1.shape[0]  # Maximum size in terms of scaling factor (not exceeding 600 pixels in height)
game_time = 120  # 2 minutes in seconds
game_state = "Greenlight"  # Initial state
game_over = False
win = False  # Variable to track win state
timer_started = False
start_time = None
game_started = False  # Track if the game has started
character_selected = False  # เช็คว่าผู้เล่นได้เลือกตัวละครหรือยัง

# Initialize webcam
cap = cv2.VideoCapture(0)  # ใช้กล้องที่ 0
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
    return movement > 5000  # กำหนดค่าขีดจำกัดว่ามีการเคลื่อนไหวหรือไม่

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
        display_text(frame, "Press 1, 2, or 3 to choose a character", (300, 360), 2, (255, 255, 255), 3)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('1'):
            character = character1
            character_selected = True
        elif key == ord('2'):
            character = character2
            character_selected = True
        elif key == ord('3'):
            character = character3
            character_selected = True
        continue

    # ถ้ายังไม่เริ่มเกม แสดงข้อความให้กด 'P' เพื่อเริ่ม
    if not game_started:
        display_text(frame, "Are you ready? Press 'P' to start", (300, 360), 2, (255, 255, 255), 3)
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('p'):  # กด 'p' เพื่อเริ่มเกม
            game_started = True
            start_time = time.time()  # เริ่มนับเวลา
        continue

    # Timer logic
    if not timer_started:
        start_time = time.time()
        timer_started = True

    elapsed_time = int(time.time() - start_time)
    remaining_time = max(game_time - elapsed_time, 0)

    # Display countdown timer
    display_text(frame, f"Time: {remaining_time // 60}:{remaining_time % 60:02}", (1000, 50), 1, (255, 255, 255), 2)

    if game_over:
        if win:
            display_text(frame, "You win! Press 'R' to restart", (400, 360), 2, (0, 255, 0), 3)
        else:
            display_text(frame, "Game Over! Press 'R' to restart", (400, 360), 2, (0, 0, 255), 3)
    else:
        # Redlight/Greenlight logic
        if elapsed_time % 10 < 5:
            game_state = "Greenlight"
        else:
            game_state = "Redlight"

        color = (0, 255, 0) if game_state == "Greenlight" else (0, 0, 255)
        display_text(frame, game_state, (50, 50), 2, color, 3)

        # ตรวจจับการเคลื่อนไหว
        movement_detected = check_movement(prev_frame, current_frame)
        if movement_detected:
            if game_state == "Redlight":
                game_over = True
            else:
                character_size = min(character_size + 0.005, max_size)

    # อัพเดทเฟรมก่อนหน้า
    prev_frame = current_frame.copy()

    # Resize character image
    character_resized = cv2.resize(character,
                                   (int(character.shape[1] * character_size), int(character.shape[0] * character_size)))

    # ตรวจสอบว่าขนาดของตัวละครไม่เกิน 600 pixels
    if character_resized.shape[0] >= 600:
        win = True
        game_over = True

    char_x = max((width - character_resized.shape[1]) // 2, 0)
    char_y = max((height - character_resized.shape[0]) // 2, 0)

    char_x_end = min(char_x + character_resized.shape[1], width)
    char_y_end = min(char_y + character_resized.shape[0], height)

    # ตรวจสอบว่าตัวละครมี alpha channel หรือไม่
    if character_resized.shape[2] == 4:  # ตรวจสอบว่ามี 4 ช่องสี (BGR + alpha)
        b, g, r, a = cv2.split(character_resized)
        alpha = a.astype(float) / 255.0  # แปลงค่าช่อง alpha เป็น float (0-1)

        # สร้างภาพพื้นหลังที่ถูกลบออกจาก alpha channel
        for c in range(3):  # สำหรับแต่ละช่องสี BGR
            frame[char_y:char_y_end, char_x:char_x_end, c] = (
                        alpha * b + (1 - alpha) * frame[char_y:char_y_end, char_x:char_x_end, c])
    else:
        frame[char_y:char_y_end, char_x:char_x_end] = character_resized[0:char_y_end - char_y, 0:char_x_end - char_x]

    try:
        frame[char_y:char_y_end, char_x:char_x_end] = character_resized[0:char_y_end - char_y, 0:char_x_end - char_x]
    except ValueError as e:
        print(f"Error placing character: {e}")

    camera_display = cv2.resize(current_frame, (320, 180))
    frame[height - 180:height, width - 320:width] = camera_display

    cv2.imshow(window_name, frame)

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r') and game_over:
        game_over = False
        win = False
        character_size = 0.1
        start_time = time.time()
        game_started = False  # Reset game_started state to ask player if they are ready
        character_selected = False  # Reset character selection

cap.release()
cv2.destroyAllWindows()
