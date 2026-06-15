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
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
# Speeds are now in pixels per second rather than pixels per frame
ball_speed = [150, 150]

paddle_height = 60
paddle_width = 5
paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
paddle_speed = [120, 300]  # [horizontal_speed, vertical_speed] in pixels per second
paddle_dx = 0
paddle_dy = 0

# Track the player's score (successful paddle bounces)
score = 0

# Game states: "MENU", "PLAYING", "GAME_OVER"
state = "MENU"

# 7. Main Game Loop
# This loop runs continuously until the game is closed.
running = True
while running:
    
    # Calculate delta time (dt): seconds elapsed since the last frame.
    # Cap it at 0.1 seconds to prevent huge physics jumps during lag spikes.
    dt = min(clock.tick(FPS) / 1000.0, 0.1)
    
    # --- A. EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            # Event handling based on current game state
            if state == "MENU":
                if event.key == pygame.K_SPACE:
                    # Reset game state and start playing
                    score = 0
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [150, 150]
                    paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
                    paddle_dx = 0
                    paddle_dy = 0
                    state = "PLAYING"
                    
            elif state == "PLAYING":
                if event.key == pygame.K_LEFT:
                    paddle_dx = -1
                elif event.key == pygame.K_RIGHT:
                    paddle_dx = 1
                elif event.key == pygame.K_UP:
                    paddle_dy = -1
                elif event.key == pygame.K_DOWN:
                    paddle_dy = 1
                    
            elif state == "GAME_OVER":
                if event.key == pygame.K_SPACE:
                    # Reset game state and restart playing
                    score = 0
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [150, 150]
                    paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
                    paddle_dx = 0
                    paddle_dy = 0
                    state = "PLAYING"

        elif event.type == pygame.KEYUP:
            if state == "PLAYING":
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    paddle_dx = 0
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    paddle_dy = 0

    # --- B. UPDATE GAME STATE ---
    if state == "PLAYING":
        # Move paddle using delta time (framerate-independent)
        paddle_pos[0] += paddle_dx * paddle_speed[0] * dt
        paddle_pos[1] += paddle_dy * paddle_speed[1] * dt

        # Keep paddle inside the movement boundaries
        if paddle_pos[1] < 0:
            paddle_pos[1] = 0
        elif paddle_pos[1] + paddle_height > SCREEN_HEIGHT:
            paddle_pos[1] = SCREEN_HEIGHT - paddle_height
        if paddle_pos[0] < 0:
            paddle_pos[0] = 0
        elif paddle_pos[0] + paddle_width > 100:
            paddle_pos[0] = 100 - paddle_width

        # Move the ball using delta time (framerate-independent)
        ball_pos[0] += ball_speed[0] * dt
        ball_pos[1] += ball_speed[1] * dt

        # Right boundary collision (Bounce back)
        if ball_pos[0] + ball_radius >= SCREEN_WIDTH:
            ball_speed[0] = -ball_speed[0]
            ball_pos[0] = SCREEN_WIDTH - ball_radius
            
        # Left boundary collision (Miss -> transitions to GAME_OVER)
        if ball_pos[0] - ball_radius <= 0:
            state = "GAME_OVER"

        # Vertical boundary collisions (Top/Bottom Bounce)
        if ball_pos[1] - ball_radius <= 0:
            ball_speed[1] = -ball_speed[1]
            ball_pos[1] = ball_radius
        elif ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
            ball_speed[1] = -ball_speed[1]
            ball_pos[1] = SCREEN_HEIGHT - ball_radius

        # Create hitboxes for collision detection
        ball_hitbox = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)
        paddle_hitbox = pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height)

        # Resolve collision with the paddle (only if the ball is moving towards it)
        if ball_hitbox.colliderect(paddle_hitbox) and ball_speed[0] < 0:
            ball_speed[0] = -ball_speed[0]
            # Push the ball out of the paddle to prevent multiple collisions/overlapping
            ball_pos[0] = paddle_pos[0] + paddle_width + ball_radius
            score += 1

    # --- C. RENDER (DRAW) SCENE ---
    screen.fill(COLOR_BG)

    if state == "MENU":
        title_surface = font_title.render("SOLO PONG", True, COLOR_TEXT)
        subtitle_surface = font_subtitle.render("Press SPACE to Start - ESC to Exit", True, COLOR_BORDER)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    elif state == "PLAYING":
        # Draw the score in the background
        score_surface = font_title.render(f"Score: {score}", True, COLOR_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_surface, score_rect)
        
        # Draw instructions
        instructions_surface = font_subtitle.render("Move paddle with Arrow Keys - Press ESC to exit", True, COLOR_BORDER)
        instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(instructions_surface, instructions_rect)

        # Draw game objects
        pygame.draw.circle(screen, COLOR_BALL, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        pygame.draw.rect(screen, COLOR_PADDLE, (paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))

    elif state == "GAME_OVER":
        title_surface = font_title.render("GAME OVER", True, COLOR_BALL)
        subtitle_surface = font_subtitle.render(f"Final Score: {score} | Press SPACE to Restart - ESC to Exit", True, COLOR_TEXT)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    # Flip the display buffer
    pygame.display.flip()

# 8. Clean up and exit
pygame.quit()
sys.exit()
