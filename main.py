import pygame
import sys

# 1. Initialize all imported pygame modules
# This must be called before using any pygame functions.
pygame.init()

# 2. Setup constants and configuration
# Having constants at the top makes it easy to adjust the game settings.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60  # Frames Per Second: controls how fast the game updates

# Color definitions (R, G, B)
COLOR_BG = (30, 30, 40)       # Sleek dark gray-blue background
COLOR_TEXT = (240, 240, 240)   # Off-white for text
COLOR_BALL = (255, 100, 100)   # Vibrant red/pink for the ball
COLOR_BORDER = (100, 200, 255) # Light blue for outline/UI highlights

# 3. Create the game window (Display surface)
# The screen is a special pygame Surface representing the visible window.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Hello World")

# 4. Create a clock object to manage frame rate
# The clock helps maintain a steady frame rate across different computer hardware.
clock = pygame.time.Clock()

# 5. Initialize fonts
# pygame.font.SysFont creates a Font object using system fonts.
# None uses the default pygame system font.
font_title = pygame.font.SysFont(None, 48)
font_subtitle = pygame.font.SysFont(None, 24)

# 6. Initialize Game State Variables
# These represent the dynamic parts of our game that change over time.
ball_radius = 20
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]  # Start ball in center
ball_speed = [5, 4]  # Speed in pixels per frame [x_speed, y_speed]

# 7. Main Game Loop
# This loop runs continuously until the game is closed.
running = True
while running:
    
    # --- A. EVENT HANDLING ---
    # The event queue captures player inputs (clicks, keypresses, window events).
    # We must process them every frame to keep the window responsive.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Player clicked the window's close (X) button
            running = False
        elif event.type == pygame.KEYDOWN:
            # A keyboard key was pressed down
            if event.key == pygame.K_ESCAPE:
                # Quit the game if Escape key is pressed
                running = False

    # --- B. UPDATE GAME STATE ---
    # Update position of the bouncing ball
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    # Handle ball collision with screen boundaries
    # Horizontal boundaries (Left/Right)
    if ball_pos[0] - ball_radius <= 0 or ball_pos[0] + ball_radius >= SCREEN_WIDTH:
        ball_speed[0] = -ball_speed[0]  # Reverse horizontal direction
        
    # Vertical boundaries (Top/Bottom)
    if ball_pos[1] - ball_radius <= 0 or ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
        ball_speed[1] = -ball_speed[1]  # Reverse vertical direction

    # --- C. RENDER (DRAW) SCENE ---
    # Pygame drawing works by layers: items drawn first are under items drawn later.
    
    # First: Clear the screen by painting it with the background color
    screen.fill(COLOR_BG)

    # Second: Render text elements
    # render() creates a new surface with the text drawn on it.
    # Arguments: (text_string, antialias_boolean, color)
    title_surface = font_title.render("Hello, Pygame!", True, COLOR_TEXT)
    subtitle_surface = font_subtitle.render("Bouncing ball demo - Press ESC to exit", True, COLOR_BORDER)

    # Position text surfaces in the center of the screen
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))

    # blit() draws the contents of one surface onto another.
    screen.blit(title_surface, title_rect)
    screen.blit(subtitle_surface, subtitle_rect)

    # Third: Draw shapes (the ball)
    # pygame.draw.circle draws a circle on a target surface.
    # Arguments: (surface, color, center_coordinates, radius)
    pygame.draw.circle(screen, COLOR_BALL, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    # Fourth: Update the display
    # This flips the back-buffer to the visible window, showing what we just drew.
    pygame.display.flip()

    # --- D. LIMIT FRAME RATE ---
    # clock.tick(FPS) pauses the loop to ensure the game doesn't run too fast.
    # It keeps the game running at a consistent speed on all machines.
    clock.tick(FPS)

# 8. Clean up and exit
# Safely close the pygame window and shut down system resources.
pygame.quit()
sys.exit()
