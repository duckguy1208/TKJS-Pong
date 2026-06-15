import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

COLOR_BG = (30, 30, 40)
COLOR_TEXT = (240, 240, 240)
COLOR_BALL = (255, 100, 100)
COLOR_BORDER = (100, 200, 255)
COLOR_PADDLE = (100, 255, 100)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Hello World")

clock = pygame.time.Clock()

font_title = pygame.font.SysFont(None, 48)
font_subtitle = pygame.font.SysFont(None, 24)

ball_radius = 20
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_speed = [150, 150]

paddle_height = 60
paddle_width = 5
paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
paddle_speed = [120, 300]
paddle_dx = 0
paddle_dy = 0

score = 0
state = "MENU"

# --- LESSON: PARTICLE SYSTEMS IN GAME ENGINES ---
# A particle system simulates organic visual effects (sparks, smoke, explosions)
# by creating a collection of independent moving shapes (particles) that evolve
# and fade away over time. Each particle is represented as a dictionary storing
# its current physical properties: position, velocity, size, and lifetime.
particles = []

def spawn_particles(x, y, color):
    # Spawning multiple particles with randomized velocities creates an explosion effect.
    for _ in range(15):
        # We randomize the directional velocities so the particles disperse outward.
        vx = random.uniform(-100, 100)
        vy = random.uniform(-100, 100)
        
        # Giving each particle a random initial size and lifetime (in seconds)
        # makes the overall explosion effect look more natural and uneven.
        size = random.uniform(3, 8)
        lifetime = random.uniform(0.3, 0.6)
        
        particles.append({
            "pos": [x, y],
            "vel": [vx, vy],
            "color": color,
            "size": size,
            "lifetime": lifetime,
            "max_lifetime": lifetime
        })

running = True
while running:
    
    dt = min(clock.tick(FPS) / 1000.0, 0.1)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            if state == "MENU":
                if event.key == pygame.K_SPACE:
                    score = 0
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [150, 150]
                    paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
                    paddle_dx = 0
                    paddle_dy = 0
                    # Clear any leftover particles when starting a new game
                    particles.clear()
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
                    score = 0
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [150, 150]
                    paddle_pos = [paddle_width, SCREEN_HEIGHT // 2 - paddle_height // 2]
                    paddle_dx = 0
                    paddle_dy = 0
                    # Clear any leftover particles when starting a new game
                    particles.clear()
                    state = "PLAYING"

        elif event.type == pygame.KEYUP:
            if state == "PLAYING":
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    paddle_dx = 0
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    paddle_dy = 0

    # --- LESSON: UPDATING PARTICLES ---
    # Every frame, we update the particles by moving them according to their velocity
    # and reducing their remaining lifetime. We iterate over a copy of the list
    # (using `particles[:]`) so we can safely remove dead particles from the
    # original list without disrupting the iteration loop.
    for p in particles[:]:
        p["pos"][0] += p["vel"][0] * dt
        p["pos"][1] += p["vel"][1] * dt
        p["lifetime"] -= dt
        if p["lifetime"] <= 0:
            particles.remove(p)

    if state == "PLAYING":
        paddle_pos[0] += paddle_dx * paddle_speed[0] * dt
        paddle_pos[1] += paddle_dy * paddle_speed[1] * dt

        if paddle_pos[1] < 0:
            paddle_pos[1] = 0
        elif paddle_pos[1] + paddle_height > SCREEN_HEIGHT:
            paddle_pos[1] = SCREEN_HEIGHT - paddle_height
        if paddle_pos[0] < 0:
            paddle_pos[0] = 0
        elif paddle_pos[0] + paddle_width > 100:
            paddle_pos[0] = 100 - paddle_width

        ball_pos[0] += ball_speed[0] * dt
        ball_pos[1] += ball_speed[1] * dt

        if ball_pos[0] + ball_radius >= SCREEN_WIDTH:
            ball_speed[0] = -ball_speed[0]
            ball_pos[0] = SCREEN_WIDTH - ball_radius
            spawn_particles(ball_pos[0] + ball_radius, ball_pos[1], COLOR_BORDER)
            
        if ball_pos[0] - ball_radius <= 0:
            spawn_particles(ball_pos[0] - ball_radius, ball_pos[1], COLOR_BALL)
            state = "GAME_OVER"

        if ball_pos[1] - ball_radius <= 0:
            ball_speed[1] = -ball_speed[1]
            ball_pos[1] = ball_radius
            spawn_particles(ball_pos[0], ball_pos[1] - ball_radius, COLOR_BORDER)
        elif ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
            ball_speed[1] = -ball_speed[1]
            ball_pos[1] = SCREEN_HEIGHT - ball_radius
            spawn_particles(ball_pos[0], ball_pos[1] + ball_radius, COLOR_BORDER)

        ball_hitbox = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)
        paddle_hitbox = pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height)

        if ball_hitbox.colliderect(paddle_hitbox) and ball_speed[0] < 0:
            ball_speed[0] = -ball_speed[0]
            ball_pos[0] = paddle_pos[0] + paddle_width + ball_radius
            score += 1
            spawn_particles(paddle_pos[0] + paddle_width, ball_pos[1], COLOR_PADDLE)

    screen.fill(COLOR_BG)

    if state == "MENU":
        title_surface = font_title.render("SOLO PONG", True, COLOR_TEXT)
        subtitle_surface = font_subtitle.render("Press SPACE to Start - ESC to Exit", True, COLOR_BORDER)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    elif state == "PLAYING":
        score_surface = font_title.render(f"Score: {score}", True, COLOR_TEXT)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_surface, score_rect)
        
        instructions_surface = font_subtitle.render("Move paddle with Arrow Keys - Press ESC to exit", True, COLOR_BORDER)
        instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(instructions_surface, instructions_rect)

        pygame.draw.circle(screen, COLOR_BALL, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        pygame.draw.rect(screen, COLOR_PADDLE, (paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))

    elif state == "GAME_OVER":
        title_surface = font_title.render("GAME OVER", True, COLOR_BALL)
        subtitle_surface = font_subtitle.render(f"Final Score: {score} | Press SPACE to Restart - ESC to Exit", True, COLOR_TEXT)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    # --- LESSON: RENDERING PARTICLES WITH FADE ---
    # To render the particles, we iterate through the active list and draw them on screen.
    # To simulate fading away, we shrink the drawn radius of each particle and shift
    # its color towards the background color (COLOR_BG) based on the particle's remaining lifetime.
    for p in particles:
        ratio = p["lifetime"] / p["max_lifetime"]
        size = max(1, int(p["size"] * ratio))
        
        r = int(COLOR_BG[0] + (p["color"][0] - COLOR_BG[0]) * ratio)
        g = int(COLOR_BG[1] + (p["color"][1] - COLOR_BG[1]) * ratio)
        b = int(COLOR_BG[2] + (p["color"][2] - COLOR_BG[2]) * ratio)
        
        pygame.draw.circle(screen, (r, g, b), (int(p["pos"][0]), int(p["pos"][1])), size)

    pygame.display.flip()

pygame.quit()
sys.exit()
