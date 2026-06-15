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
COLOR_PADDLE = (100, 255, 100) # Light green for the paddle

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
ball_speed = [2, 2]  # Speed in pixels per frame [x_speed, y_speed]


paddle_height = 60
paddle_width = 5
paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
paddle_speed = [2, 5]
paddle_dx = 0
paddle_dy = 0

# Track the player's score (successful paddle bounces)
score = 0

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
            elif event.key == pygame.K_LEFT:
                paddle_dx = -paddle_speed[0]
            elif event.key == pygame.K_RIGHT:
                paddle_dx = paddle_speed[0]
            elif event.key == pygame.K_UP:
                paddle_dy = -paddle_speed[1]
            elif event.key == pygame.K_DOWN:
                paddle_dy = paddle_speed[1]

        elif event.type == pygame.KEYUP:
            # A keyboard key was released
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                paddle_dx = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                paddle_dy = 0

    paddle_pos[0] += paddle_dx
    paddle_pos[1] += paddle_dy

    # --- B. UPDATE GAME STATE ---
    # Update position of the bouncing ball
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    # Handle ball collision with screen boundaries
    # Right boundary (Bounce back)
    if ball_pos[0] + ball_radius >= SCREEN_WIDTH:
        ball_speed[0] = -ball_speed[0]
        
    # Left boundary (Miss - reset the ball and score)
    if ball_pos[0] - ball_radius <= 0:
        ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        ball_speed = [2, 2]
        score = 0

    # Vertical boundaries (Top/Bottom)
    if ball_pos[1] - ball_radius <= 0 or ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
        ball_speed[1] = -ball_speed[1]  # Reverse vertical direction

    # Keep paddle inside the screen
    if paddle_pos[1] < 0:
        paddle_pos[1] = 0
    elif paddle_pos[1] + paddle_height > SCREEN_HEIGHT:
        paddle_pos[1] = SCREEN_HEIGHT - paddle_height
    if paddle_pos[0] < 0:
        paddle_pos[0] = 0
    elif paddle_pos[0] + paddle_width > 100:
        paddle_pos[0] = 100 - paddle_width


    # Create hitboxes for collision detection
    ball_hitbox = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)
    paddle_hitbox = pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height)

    # Resolve collision with the paddle (only if the ball is moving towards it)
    if ball_hitbox.colliderect(paddle_hitbox) and ball_speed[0] < 0:
        ball_speed[0] = -ball_speed[0]
        # Adjust position to prevent the ball from overlapping and sticking to the paddle
        ball_pos[0] = paddle_pos[0] + paddle_width + ball_radius
        score += 1


    # --- C. RENDER (DRAW) SCENE ---
    # Pygame drawing works by layers: items drawn first are under items drawn later.
    
    # First: Clear the screen by painting it with the background color
    screen.fill(COLOR_BG)

    # Second: Render text elements
    # Render the current score and updated gameplay instructions.
    title_surface = font_title.render(f"Score: {score}", True, COLOR_TEXT)
    subtitle_surface = font_subtitle.render("Move paddle with Arrow Keys - Press ESC to exit", True, COLOR_BORDER)

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

    # Fourth: Draw the paddle
    pygame.draw.rect(screen, COLOR_PADDLE, (paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))

    # Fifth: Update the display
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
