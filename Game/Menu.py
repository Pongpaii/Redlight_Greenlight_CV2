import pygame
import subprocess  # ใช้สำหรับเปิดไฟล์ .py ภายนอก
import SceneManager
import  mediapipe


def Menu():
    # Initialize Pygame
    pygame.init()
    pygame.event.clear()

    # Create Window/Display
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Squid Game")

    # Initialize Clock for FPS
    fps = 30
    clock = pygame.time.Clock()

    # Load Images
    imgBG = pygame.image.load("Resources/Menu/BG.jpg").convert()
    play_button_img = pygame.image.load("Resources/Menu/Play_button.png").convert_alpha()

    # Resize the play button image to make it smaller
    play_button_small = pygame.transform.scale(play_button_img, (100, 50))  # ปรับขนาดเป็น 100x50 พิกเซล
    play_button_rect = play_button_small.get_rect(center=(width // 2, height // 2))

    # Main loop
    start = True
    while start:
        # Get Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    # เมื่อกดปุ่ม play จะเปิดไฟล์ redlightgreenV2.py
                    subprocess.Popen(["python", "redlightgreenV2.py"])
                    start = False

        # Apply Logic
        window.blit(imgBG, (0, 0))
        window.blit(play_button_small, play_button_rect)

        # Update Display
        pygame.display.update()

        # Set FPS
        clock.tick(fps)


if __name__ == "__main__":
    Menu()
