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

game_mode = "BREAKOUT"
state = "MENU"
score = 0
player_score = 0
ai_score = 0

ball_radius = 12
ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_speed = [150, -200]

paddle_height = 12
paddle_width = 120
paddle_pos = [SCREEN_WIDTH // 2 - paddle_width // 2, SCREEN_HEIGHT - paddle_height - 20]
paddle_speed = [350, 350]
paddle_dx = 0
paddle_dy = 0

ai_paddle_width = 12
ai_paddle_height = 100
ai_paddle_pos = [SCREEN_WIDTH - 20 - ai_paddle_width, SCREEN_HEIGHT // 2 - ai_paddle_height // 2]
ai_paddle_speed = 220

# --- LESSON: BREAKOUT BRICK GRID SETUP ---
# In grid-based games like Breakout, we dynamically generate a layout of bricks.
# Each brick is stored as a dictionary containing a Pygame Rect object (for collision checks)
# and a specific color based on its row, giving the classic retro arcade look.
bricks = []

def init_bricks():
    bricks.clear()
    brick_width = 72
    brick_height = 20
    x_gap = 6
    y_gap = 6
    top_offset = 80
    left_offset = 12
    
    row_colors = [
        (255, 100, 100),
        (255, 150, 50),
        (255, 220, 50),
        (100, 255, 100),
        (100, 200, 255)
    ]
    
    for row in range(5):
        color = row_colors[row]
        for col in range(10):
            x = left_offset + col * (brick_width + x_gap)
            y = top_offset + row * (brick_height + y_gap)
            bricks.append({
                "rect": pygame.Rect(x, y, brick_width, brick_height),
                "color": color
            })

def init_game():
    global score, player_score, ai_score, ball_pos, ball_speed
    global paddle_width, paddle_height, paddle_pos, paddle_dx, paddle_dy
    global ai_paddle_pos
    
    particles.clear()
    
    if game_mode == "BREAKOUT":
        score = 0
        paddle_width = 120
        paddle_height = 12
        paddle_pos = [SCREEN_WIDTH // 2 - paddle_width // 2, SCREEN_HEIGHT - paddle_height - 20]
        paddle_dx = 0
        paddle_dy = 0
        ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        ball_speed = [150, -200]
        init_bricks()
    elif game_mode == "PONG":
        player_score = 0
        ai_score = 0
        paddle_width = 12
        paddle_height = 100
        paddle_pos = [20, SCREEN_HEIGHT // 2 - paddle_height // 2]
        paddle_dx = 0
        paddle_dy = 0
        ai_paddle_pos = [SCREEN_WIDTH - 20 - ai_paddle_width, SCREEN_HEIGHT // 2 - ai_paddle_height // 2]
        ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        ball_speed = [-250, random.choice([-120, 120])]
        bricks.clear()

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
        vx = random.uniform(-150, 150)
        vy = random.uniform(-150, 150)
        
        # Giving each particle a random initial size and lifetime (in seconds)
        # makes the overall explosion effect look more natural and uneven.
        size = random.uniform(2, 6)
        lifetime = random.uniform(0.2, 0.5)
        
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
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    game_mode = "PONG" if game_mode == "BREAKOUT" else "BREAKOUT"
                elif event.key == pygame.K_SPACE:
                    init_game()
                    state = "PLAYING"
                    
            elif state == "PLAYING":
                if game_mode == "BREAKOUT":
                    if event.key == pygame.K_LEFT:
                        paddle_dx = -1
                    elif event.key == pygame.K_RIGHT:
                        paddle_dx = 1
                elif game_mode == "PONG":
                    if event.key == pygame.K_UP:
                        paddle_dy = -1
                    elif event.key == pygame.K_DOWN:
                        paddle_dy = 1
                    
            elif state == "GAME_OVER" or state == "WIN":
                if event.key == pygame.K_SPACE:
                    init_game()
                    state = "PLAYING"

        elif event.type == pygame.KEYUP:
            if state == "PLAYING":
                if game_mode == "BREAKOUT":
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        paddle_dx = 0
                elif game_mode == "PONG":
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
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
        if game_mode == "BREAKOUT":
            paddle_pos[0] += paddle_dx * paddle_speed[0] * dt

            if paddle_pos[0] < 0:
                paddle_pos[0] = 0
            elif paddle_pos[0] + paddle_width > SCREEN_WIDTH:
                paddle_pos[0] = SCREEN_WIDTH - paddle_width

            ball_pos[0] += ball_speed[0] * dt
            ball_pos[1] += ball_speed[1] * dt

            if ball_pos[0] - ball_radius <= 0:
                ball_speed[0] = -ball_speed[0]
                ball_pos[0] = ball_radius
                spawn_particles(ball_pos[0] - ball_radius, ball_pos[1], COLOR_BORDER)
            elif ball_pos[0] + ball_radius >= SCREEN_WIDTH:
                ball_speed[0] = -ball_speed[0]
                ball_pos[0] = SCREEN_WIDTH - ball_radius
                spawn_particles(ball_pos[0] + ball_radius, ball_pos[1], COLOR_BORDER)
                
            if ball_pos[1] - ball_radius <= 0:
                ball_speed[1] = -ball_speed[1]
                ball_pos[1] = ball_radius
                spawn_particles(ball_pos[0], ball_pos[1] - ball_radius, COLOR_BORDER)

            if ball_pos[1] + ball_radius >= SCREEN_HEIGHT:
                spawn_particles(ball_pos[0], ball_pos[1] + ball_radius, COLOR_BALL)
                state = "GAME_OVER"

            ball_hitbox = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)
            paddle_hitbox = pygame.Rect(paddle_pos[0], paddle_pos[1], paddle_width, paddle_height)

            # --- LESSON: PADDLE ANGLE DEFLECTION ---
            # Instead of a simple vertical bounce, we calculate where the ball strikes
            # the paddle relative to its center. This normalized value (-1.0 at left edge,
            # +1.0 at right edge) is used to deflect the horizontal velocity, giving the player
            # control over directing the ball to target specific bricks.
            if ball_hitbox.colliderect(paddle_hitbox) and ball_speed[1] > 0:
                ball_speed[1] = -ball_speed[1]
                ball_pos[1] = paddle_pos[1] - ball_radius
                
                paddle_center = paddle_pos[0] + paddle_width / 2
                hit_offset = ball_pos[0] - paddle_center
                normalized_hit = hit_offset / (paddle_width / 2)
                
                ball_speed[0] = normalized_hit * 250
                spawn_particles(ball_pos[0], paddle_pos[1], COLOR_PADDLE)

            # --- LESSON: RECT CLIP COLLISION RESOLUTION ---
            # To make the ball bounce realistically off a brick, we need to know whether
            # it hit the top/bottom edge or the left/right side. Using Pygame's `Rect.clip()`
            # method returns the overlapping area of the collision. If the overlap is wider
            # than it is tall, the collision happened vertically (top/bottom), so we reverse vy.
            # Otherwise, the collision was horizontal (sides), so we reverse vx.
            for brick in bricks[:]:
                if ball_hitbox.colliderect(brick["rect"]):
                    overlap = ball_hitbox.clip(brick["rect"])
                    if overlap.width > overlap.height:
                        ball_speed[1] = -ball_speed[1]
                    else:
                        ball_speed[0] = -ball_speed[0]
                    
                    spawn_particles(brick["rect"].centerx, brick["rect"].centery, brick["color"])
                    bricks.remove(brick)
                    score += 10
                    
            if len(bricks) == 0:
                state = "WIN"

        elif game_mode == "PONG":
            paddle_pos[1] += paddle_dy * paddle_speed[1] * dt
            if paddle_pos[1] < 0:
                paddle_pos[1] = 0
            elif paddle_pos[1] + paddle_height > SCREEN_HEIGHT:
                paddle_pos[1] = SCREEN_HEIGHT - paddle_height

            # --- LESSON: AI OPPONENT LOGIC ---
            # To simulate a computer opponent, the AI paddle compares its vertical center
            # with the ball's vertical position. It moves UP if the ball is above it,
            # and DOWN if the ball is below it. We introduce a small deadzone (+/- 10 pixels)
            # and limit the AI's speed to make it beatable and prevent rapid jittering.
            ai_center = ai_paddle_pos[1] + ai_paddle_height / 2
            if ball_pos[1] < ai_center - 10:
                ai_paddle_dy = -1
            elif ball_pos[1] > ai_center + 10:
                ai_paddle_dy = 1
            else:
                ai_paddle_dy = 0
                
            ai_paddle_pos[1] += ai_paddle_dy * ai_paddle_speed * dt
            if ai_paddle_pos[1] < 0:
                ai_paddle_pos[1] = 0
            elif ai_paddle_pos[1] + ai_paddle_height > SCREEN_HEIGHT:
                ai_paddle_pos[1] = SCREEN_HEIGHT - ai_paddle_height

            ball_pos[0] += ball_speed[0] * dt
            ball_pos[1] += ball_speed[1] * dt

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
            ai_paddle_hitbox = pygame.Rect(ai_paddle_pos[0], ai_paddle_pos[1], ai_paddle_width, ai_paddle_height)

            if ball_hitbox.colliderect(paddle_hitbox) and ball_speed[0] < 0:
                ball_speed[0] = -ball_speed[0]
                ball_pos[0] = paddle_pos[0] + paddle_width + ball_radius
                
                hit_offset = ball_pos[1] - (paddle_pos[1] + paddle_height / 2)
                normalized_hit = hit_offset / (paddle_height / 2)
                ball_speed[1] = normalized_hit * 250
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_PADDLE)

            if ball_hitbox.colliderect(ai_paddle_hitbox) and ball_speed[0] > 0:
                ball_speed[0] = -ball_speed[0]
                ball_pos[0] = ai_paddle_pos[0] - ball_radius
                
                hit_offset = ball_pos[1] - (ai_paddle_pos[1] + ai_paddle_height / 2)
                normalized_hit = hit_offset / (ai_paddle_height / 2)
                ball_speed[1] = normalized_hit * 250
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BORDER)

            if ball_pos[0] - ball_radius <= 0:
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BALL)
                ai_score += 1
                if ai_score >= 5:
                    score = f"{player_score} - {ai_score}"
                    state = "GAME_OVER"
                else:
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [250, random.choice([-120, 120])]

            elif ball_pos[0] + ball_radius >= SCREEN_WIDTH:
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BALL)
                player_score += 1
                if player_score >= 5:
                    score = f"{player_score} - {ai_score}"
                    state = "WIN"
                else:
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [-250, random.choice([-120, 120])]

    screen.fill(COLOR_BG)

    if state == "MENU":
        title_surface = font_title.render("ARCADE CABINET", True, COLOR_TEXT)
        mode_surface = font_title.render(f"< Mode: {game_mode} >", True, COLOR_PADDLE)
        subtitle_surface = font_subtitle.render("Press UP/DOWN to Switch Mode - Press SPACE to Start", True, COLOR_BORDER)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        mode_rect = mode_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        
        screen.blit(title_surface, title_rect)
        screen.blit(mode_surface, mode_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    elif state == "PLAYING":
        if game_mode == "BREAKOUT":
            score_surface = font_title.render(f"Score: {score}", True, COLOR_TEXT)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(score_surface, score_rect)
            
            instructions_surface = font_subtitle.render("Move paddle with Left/Right Keys - Press ESC to exit", True, COLOR_BORDER)
            instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(instructions_surface, instructions_rect)

            pygame.draw.circle(screen, COLOR_BALL, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
            pygame.draw.rect(screen, COLOR_PADDLE, (paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))

            for brick in bricks:
                pygame.draw.rect(screen, brick["color"], brick["rect"])
                
        elif game_mode == "PONG":
            score_surface = font_title.render(f"{player_score}   {ai_score}", True, COLOR_TEXT)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
            screen.blit(score_surface, score_rect)
            
            for y in range(0, SCREEN_HEIGHT, 30):
                pygame.draw.rect(screen, (60, 60, 80), (SCREEN_WIDTH // 2 - 2, y, 4, 15))
            
            instructions_surface = font_subtitle.render("Move paddle with Up/Down Keys - Press ESC to exit", True, COLOR_BORDER)
            instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(instructions_surface, instructions_rect)

            pygame.draw.circle(screen, COLOR_BALL, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
            pygame.draw.rect(screen, COLOR_PADDLE, (paddle_pos[0], paddle_pos[1], paddle_width, paddle_height))
            pygame.draw.rect(screen, COLOR_TEXT, (ai_paddle_pos[0], ai_paddle_pos[1], ai_paddle_width, ai_paddle_height))

    elif state == "GAME_OVER":
        title_surface = font_title.render("GAME OVER", True, COLOR_BALL)
        
        if game_mode == "BREAKOUT":
            sub_text = f"Final Score: {score} | Press SPACE to Restart - ESC to Exit"
        else:
            sub_text = f"Final Score: {score} (AI Wins) | Press SPACE to Restart - ESC to Exit"
            
        subtitle_surface = font_subtitle.render(sub_text, True, COLOR_TEXT)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)

    elif state == "WIN":
        title_surface = font_title.render("YOU WIN!", True, COLOR_PADDLE)
        
        if game_mode == "BREAKOUT":
            sub_text = f"Final Score: {score} | Press SPACE to Play Again - ESC to Exit"
        else:
            sub_text = f"Final Score: {score} (You Beat AI!) | Press SPACE to Play Again - ESC to Exit"
            
        subtitle_surface = font_subtitle.render(sub_text, True, COLOR_TEXT)
        
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
