import cv2
import numpy as np
import time
import pygame  # สำหรับเล่นเสียง

# Initial settings
window_name = "Redlight Greenlight Game"
width, height = 1280, 720
bg_image = cv2.imread('Resources/Menu/Bg.jpeg')
bg_image = cv2.resize(bg_image, (width, height))  # ปรับขนาดภาพพื้นหลัง

character = cv2.imread('Resources/Menu/Char1.png')
character1 = cv2.imread('Resources/Menu/Char1.png')
character2 = cv2.imread('Resources/Menu/Kai_Onstove.png')
character3 = cv2.imread('Resources/Menu/Bada_Onstove.png')
character_size = 0.1  # Initial size of the character (very small)
max_size = 600 / character.shape[0]  # Maximum size in terms of scaling factor (not exceeding 600 pixels in height)
game_time = 120  # 2 minutes in seconds
game_state = "Greenlight"  # Initial state
game_over = False
win = False  # Variable to track win state
timer_started = False
start_time = None
game_started = False  # Track if the game has started
selected_button = None  # Track selected button

# Initialize pygame for sound effects
pygame.mixer.init()
redlight_sound = pygame.mixer.Sound('Resources/Sounds/redlight.mp3')
greenlight_sound = pygame.mixer.Sound('Resources/Sounds/greenlight.mp3')
gameover_sound = pygame.mixer.Sound('Resources/Sounds/gameover.mp3')
win_sound = pygame.mixer.Sound('Resources/Sounds/win.mp3')

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ไม่สามารถเปิดกล้องได้")
    exit()

def check_movement(prev_frame, current_frame, threshold=1000):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, curr_gray)
    _, diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    movement_score = np.sum(diff)
    return movement_score > threshold

def display_text(frame, text, position, font_scale=1, color=(255, 255, 255), thickness=2):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def add_button(frame, image, position, size=(150, 140), selected=False):
    button = cv2.imread(image)
    button = cv2.resize(button, size)
    x, y = position
    if selected:
        cv2.rectangle(frame, (x, y), (x + size[0], y + size[1]), (0, 255, 0), 3)  # แสดงกรอบถ้าถูกเลือก
    frame[y:y+size[1], x:x+size[0]] = button

ret, prev_frame = cap.read()
if not ret:
    print("ไม่สามารถอ่านเฟรมจากกล้องได้")
    cap.release()
    exit()

button_positions = [(width // 2 - 250, height // 2 - 70),
                    (width // 2 - 75, height // 2 - 70),
                    (width // 2 + 100, height // 2 - 70)]
button_images = ['Resources/Menu/player1.png', 'Resources/Menu/player2.png', 'Resources/Menu/player3.png']

while True:
    ret, current_frame = cap.read()
    if not ret:
        print("ไม่สามารถอ่านเฟรมจากกล้องได้")
        break

    frame = bg_image.copy()

    if not game_started:
        display_text(frame, "Are you ready? Press 'P' to start", (300, 360), 2, (255, 255, 255), 3)
        for i, position in enumerate(button_positions):
            add_button(frame, button_images[i], position, selected=(selected_button == i))
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('p'):
            game_started = True
            start_time = time.time()
        elif key == ord('1'):
            selected_button = 0
        elif key == ord('2'):
            selected_button = 1
        elif key == ord('3'):
            selected_button = 2
        continue

    if not timer_started:
        start_time = time.time()
        timer_started = True

    elapsed_time = int(time.time() - start_time)
    remaining_time = max(game_time - elapsed_time, 0)
    display_text(frame, f"Time: {remaining_time // 60}:{remaining_time % 60:02}", (1000, 50), 1, (255, 255, 255), 2)

    if game_over:
        if win:
            display_text(frame, "You win! Press 'R' to restart", (400, 360), 2, (0, 255, 0), 3)
        else:
            display_text(frame, "Game Over! Press 'R' to restart", (400, 360), 2, (0, 0, 255), 3)
    else:
        if elapsed_time % 10 < 5:
            if game_state != "Greenlight":
                pygame.mixer.Sound.play(greenlight_sound)
            game_state = "Greenlight"
        else:
            if game_state != "Redlight":
                pygame.mixer.Sound.play(redlight_sound)
            game_state = "Redlight"

        color = (0, 255, 0) if game_state == "Greenlight" else (0, 0, 255)
        display_text(frame, game_state, (50, 50), 2, color, 3)

        movement_detected = check_movement(prev_frame, current_frame)
        if movement_detected:
            if game_state == "Redlight":
                game_over = True
                pygame.mixer.Sound.play(gameover_sound)
            else:
                character_size = min(character_size + 0.0005, max_size)

    prev_frame = current_frame.copy()

    character_resized = cv2.resize(character, (int(character.shape[1] * character_size), int(character.shape[0] * character_size)))

    if character_resized.shape[0] >= 600:
        win = True
        game_over = True
        pygame.mixer.Sound.play(win_sound)

    char_x = max((width - character_resized.shape[1]) // 2, 0)
    char_y = max((height - character_resized.shape[0]) // 2, 0)
    char_x_end = min(char_x + character_resized.shape[1], width)
    char_y_end = min(char_y + character_resized.shape[0], height)

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
        game_started = False

cap.release()
cv2.destroyAllWindows()
