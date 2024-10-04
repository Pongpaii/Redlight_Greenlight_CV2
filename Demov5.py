import cv2
import numpy as np
import time
import random  # นำเข้าโมดูลสำหรับการสุ่ม
import pygame
# Initialize variables
current_game_state = "Greenlight"  # เพิ่มบรรทัดนี้เพื่อประกาศตัวแปร
character = None
character_size = 0.1  # Initial size of the character (very small)

# กำหนดเวลาสุ่มเริ่มต้น
greenlight_duration = random.randint(1, 4)  # 3 ถึง 6 วินาที
redlight_duration = random.randint(2, 4)  # 2 ถึง 4 วินาที
next_state_change = time.time() + greenlight_duration  # ตั้งเวลาเปลี่ยนสถานะเริ่มต้น


def draw_progress_bar(frame, current_size, min_size, max_size, bar_width=468, bar_height=20, position=(400, 680),
                      bar_color=(6, 96, 228), bg_color=(184, 194, 210)):
    # คำนวณเปอร์เซ็นต์ความคืบหน้าจากขนาดปัจจุบัน
    progress = (current_size - min_size) / (max_size - min_size)
    progress = max(0, min(progress, 1))  # จำกัดค่าอยู่ในช่วง 0 ถึง 1

    # วาดพื้นหลังของแถบ
    cv2.rectangle(frame, position, (position[0] + bar_width, position[1] + bar_height), bg_color, -1)

    # วาดแถบความคืบหน้า
    filled_width = int(bar_width * progress)
    cv2.rectangle(frame, position, (position[0] + filled_width, position[1] + bar_height), bar_color, -1)


pygame.mixer.init()
red_light_sound = pygame.mixer.Sound('Resources/Sounds/redLight.mp3')
green_light_sound = pygame.mixer.Sound('Resources/Sounds/greenLight.mp3')
you_lose_sound = pygame.mixer.Sound('Resources/Sounds/gameover2.wav')
you_win_sound = pygame.mixer.Sound('Resources/Sounds/win2.wav')
# Initialize flags to track if sounds have been played
win_sound_played = False
lose_sound_played = False


# Function to display text on the frame
def display_text(frame, text, position, font_scale=1, color=(255, 255, 255), thickness=2):
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)


# Function for countdown to main menu
def countdown_to_main_menu(frame, countdown_seconds=2):
    for i in range(countdown_seconds, 0, -1):
        frame_copy = frame.copy()  # Create a copy of the frame
        display_text(frame_copy, f"Returning to main menu in {i} seconds...", (250, 500), 2, (255, 255, 255), 3)
        cv2.imshow(window_name, frame_copy)
        cv2.waitKey(1000)  # Wait 1 second for each countdown


# Function to check movement between frames
def check_movement(prev_frame, current_frame, threshold=25):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_gray, current_gray)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    movement = np.sum(thresh) / 255
    return movement > 5000  # Threshold for movement detection


# Initial settings
window_name = "Redlight Greenlight Game"
width, height = 1280, 720
bg_image = cv2.imread('Resources/Menu/BG_Snow.jpg')
bg_snow = cv2.imread('Resources/Menu/BG_night.jpg')
bg_play = cv2.imread('Resources/Menu/BG_Play1.jpg')
bg_image = cv2.resize(bg_image, (width, height))  # Resize background image
# Load shop background
background_shop = cv2.imread('Resources/Menu/choose item.jpg')
background_shop = cv2.resize(background_shop, (width, height))  # Resize shop background
# Character selection buttons
player_button_images = ['Resources/Menu/player1.png', 'Resources/Menu/player2.png', 'Resources/Menu/player3.png',
                        'Resources/Menu/player4.png', 'Resources/Menu/player5.png']  # Updated for 5 characters
# Load back and front images
back_image = cv2.imread('Resources/Menu/gl.png', cv2.IMREAD_UNCHANGED)
front_red_image = cv2.imread('Resources/Menu/rl.png', cv2.IMREAD_UNCHANGED)
# Resize back and front images (optional, adjust as needed)
back_image = cv2.resize(back_image, (300, 300))  # Resize to fit on the left
front_red_image = cv2.resize(front_red_image, (300, 300))  # Resize to fit on the left

# Charactersq
character1 = cv2.imread('Resources/Menu/c1.png', cv2.IMREAD_UNCHANGED)
character2 = cv2.imread('Resources/Menu/c2.png', cv2.IMREAD_UNCHANGED)
character3 = cv2.imread('Resources/Menu/c3.png', cv2.IMREAD_UNCHANGED)
character4 = cv2.imread('Resources/Menu/c4.png', cv2.IMREAD_UNCHANGED)
character5 = cv2.imread('Resources/Menu/c5.png', cv2.IMREAD_UNCHANGED)
# Store characters in a list for easy access
characters = [character1, character2, character3, character4, character5]
# Load selection screen background
background_selection_screen = cv2.imread('Resources/Menu/choosechar.png')
background_selection_screen = cv2.resize(background_selection_screen, (width, height))  # Resize selection screen

# Load status bar image
status_bar = cv2.imread('Resources/Menu/statusbar.jpeg')
status_bar_resized = cv2.resize(status_bar, (474, 29))  # Resize status bar
# Load Ptoplay background image
ptoplay_image = cv2.imread('Resources/Menu/Ptoplay.png')
ptoplay_image = cv2.resize(ptoplay_image, (width, height))  # Resize to 1280x720

# Initialize variables
character = None
character_size = 0.1  # Initial size of the character (very small)
max_size = 600 / character1.shape[0]  # Maximum size scaling factor
game_time = 120  # 2 minutes in seconds
game_state = "Selection"  # Initial state set to Selection
game_over = False
win = False  # Variable to track win state
timer_started = False
start_time = None
game_started = False  # Track if the game has started
character_selected = False  # Check if the player has selected a character

# Coin system
coins = 10  # Initialize total coins (set to 10 for testing)

# Speed boost variables
speed_boost_active = False
speed_boost_end_time = None
speed_boost_cost = 20  # Set cost of speed boost to 20 coins
speed_boost_used = False  # Flag to check if speed boost has been used

# Initialize webcam
cap = cv2.VideoCapture(0)  # Use camera 0
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Read the first frame from the camera
ret, prev_frame = cap.read()
if not ret:
    print("Cannot read frame from camera")
    cap.release()
    exit()

# Main game loop
while True:
    ret, current_frame = cap.read()
    if not ret:
        print("Cannot read frame from camera")
        break

    frame = bg_image.copy()

    if game_state == "Selection":
        # Display character selection screen
        frame = background_selection_screen.copy()

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('1'):
            character = character1
            character_selected = True
            game_state = "Shop"  # Transition to Shop state
        elif key == ord('2'):
            character = character2
            character_selected = True
            game_state = "Shop"
        elif key == ord('3'):
            character = character3
            character_selected = True
            game_state = "Shop"
        elif key == ord('4'):
            character = character4
            character_selected = True
            game_state = "Shop"
        elif key == ord('5'):
            character = character5
            character_selected = True
            game_state = "Shop"
        continue

    # Shop state
    elif game_state == "Shop":
        # Display Shop screen
        frame = background_shop.copy()  # Use the shop background image
        display_text(frame, f"  : {coins}", (50, 50), 1, (255, 255, 255), 2)  # Display coins

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF

        if key == ord('s') or key == ord('S'):
            if coins >= speed_boost_cost and not speed_boost_used:
                coins -= speed_boost_cost
                speed_boost_active = True
                speed_boost_end_time = time.time() + 3  # Speed boost lasts for 3 seconds
                speed_boost_used = True  # Set flag to true so it can't be bought again
                display_text(frame, "Speed Boost Activated!", (300, 500), 1, (0, 255, 0), 2)
                cv2.imshow(window_name, frame)
                cv2.waitKey(2000)  # Display message for 2 seconds
                game_state = "Play"  # Proceed to Play state
            else:
                if speed_boost_used:
                    display_text(frame, "Speed Boost already used!", (400, 500), 1, (0, 0, 255), 2)
                else:
                    display_text(frame, "Not enough coins!", (400, 500), 1, (0, 0, 255), 2)
                cv2.imshow(window_name, frame)
                cv2.waitKey(2000)  # Display message for 2 seconds
        elif key == ord('t') or key == ord('T'):
            game_state = "Play"  # Skip Shop and proceed to Play
        elif key == ord('p') or key == ord('P'):
            game_state = "Play"  # Proceed to Play without buying
        continue

    elif game_state == "Play":
        draw_progress_bar(frame, character_size, 0.1, max_size)

        # If the game hasn't started yet, display the prompt to start
        if not game_started:
            frame = ptoplay_image.copy()  # ใช้ภาพ Ptoplay เป็นพื้นหลัง
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(30) & 0xFF
            if key == ord('p') or key == ord('P'):  # Press 'P' to start the game
                if bg_image is None or np.array_equal(bg_image, cv2.imread('Resources/Menu/BG_Snow.jpg')):
                    bg_image = cv2.imread('Resources/Menu/BG_Play1.jpg')
                else:
                    bg_image = cv2.imread('Resources/Menu/BG_Snow.jpg')
                game_started = True
                start_time = time.time()  # Start the timer
            continue

        # Timer logic
        if not timer_started:
            start_time = time.time()
            timer_started = True

        elapsed_time = int(time.time() - start_time)
        remaining_time = max(game_time - elapsed_time, 0)

        # Check if game time is over
        if remaining_time == 0:
            game_over = True

        # Handle speed boost duration
        if speed_boost_active:
            if time.time() >= speed_boost_end_time:
                speed_boost_active = False  # Deactivate speed boost

        # Display countdown timer
        display_text(frame, f"Time: {remaining_time // 60}:{remaining_time % 60:02}", (1000, 50), 1, (255, 255, 255), 2)

        if game_over:
            if win:
                if not win_sound_played:  # Play the sound only if it hasn't been played
                    pygame.mixer.Sound.play(you_win_sound)
                    win_sound_played = True  # Set flag to True so it doesn't play again
                coins += 10  # Player wins and gets 10 coins
                display_text(frame, "You win! Returning to main menu...", (200, 360), 2, (0, 255, 0), 3)
                cv2.imshow(window_name, frame)
                countdown_to_main_menu(frame)  # Call countdown function
                # Reset all variables after winning
                character_selected = False
                game_started = False
                timer_started = False
                win = False
                game_over = False
                game_state = "Selection"  # Return to Selection state
                character_size = 0.1
                start_time = None
                win_sound_played = False  # Reset sound flag after game resets
            else:
                if not lose_sound_played:  # Play the sound only if it hasn't been played
                    pygame.mixer.Sound.play(you_lose_sound)
                    lose_sound_played = True  # Set flag to True so it doesn't play again
                display_text(frame, "Game Over! Press 'R' to restart", (200, 360), 2, (0, 0, 255), 3)
                cv2.imshow(window_name, frame)

        else:
            # Redlight/Greenlight logic
            if elapsed_time % (greenlight_duration + redlight_duration) < greenlight_duration:
                if current_game_state != "Greenlight":
                    pygame.mixer.Sound.play(green_light_sound)  # เล่นเสียง Greenlight
                current_game_state = "Greenlight"
                side_image = back_image  # Use Back.PNG during Greenlight
            else:
                if current_game_state != "Redlight":
                    pygame.mixer.Sound.play(red_light_sound)  # เล่นเสียง Redlight
                current_game_state = "Redlight"
                side_image = front_red_image  # Use Front_red.PNG during Redlight

            # Display the appropriate image at the bottom-left side of the screen
            img_height, img_width = side_image.shape[:2]
            x_position = 0  # ชิดขอบซ้าย
            y_position = height - img_height  # ชิดขอบล่าง
            if side_image.shape[2] == 4:  # Check for alpha channel
                # Split the image into color and alpha channels
                b, g, r, a = cv2.split(side_image)
                overlay = cv2.merge((b, g, r))
                mask = a.astype(float) / 255.0
                for c in range(3):  # For each color channel
                    frame[y_position:y_position + img_height, x_position:x_position + img_width, c] = (
                            mask * overlay[:, :, c] +
                            (1 - mask) * frame[y_position:y_position + img_height, x_position:x_position + img_width, c]
                    )
            else:
                frame[y_position:y_position + img_height, x_position:x_position + img_width] = side_image

            # Detect movement
            movement_detected = check_movement(prev_frame, current_frame)
            if movement_detected:
                if current_game_state == "Redlight":
                    game_over = True
                else:
                    # Increase character size faster if speed boost is active
                    growth_rate = 0.0005 if speed_boost_active else 0.005  # ลดการขยายให้ช้าลง
                    character_size = min(character_size + growth_rate, max_size)

            # Update previous frame
            prev_frame = current_frame.copy()

            # Resize character image
            character_resized = cv2.resize(character,
                                           (int(character.shape[1] * character_size),
                                            int(character.shape[0] * character_size)))

            # Check if character size exceeds maximum
            if character_resized.shape[0] >= 600:
                win = True
                game_over = True
                character_size = 0.1

            # Calculate character position
            char_x = max((width - character_resized.shape[1]) // 2, 0)
            char_y = max((height - character_resized.shape[0]) // 2, 0)

            char_x_end = min(char_x + character_resized.shape[1], width)
            char_y_end = min(char_y + character_resized.shape[0], height)

            # Overlay character with transparency if alpha channel exists
            if character_resized.shape[2] == 4:  # Check for alpha channel
                b, g, r, a = cv2.split(character_resized)
                alpha = a.astype(float) / 255.0  # Normalize alpha channel

                for c in range(3):  # For each color channel
                    frame[char_y:char_y_end, char_x:char_x_end, c] = (
                            alpha * character_resized[:, :, c] +
                            (1 - alpha) * frame[char_y:char_y_end, char_x:char_x_end, c]
                    )
            else:
                frame[char_y:char_y_end, char_x:char_x_end] = character_resized

        # Display camera feed in the corner
        camera_display = cv2.resize(current_frame, (320, 180))
        frame[height - 180:height, width - 320:width] = camera_display

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r') and game_over:
            # Reset game variables
            game_over = False
            win = False
            character_size = 0.1
            start_time = time.time()
            game_started = False
            game_state = "Selection"  # Return to Selection state
            win_sound_played = False  # Reset win sound flag
            lose_sound_played = False  # Reset lose sound flag

cap.release()
cv2.destroyAllWindows()
