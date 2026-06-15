import pygame
import sys
import random
import json
import os

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
paddle_height = 12
paddle_width = 120
paddle_speed = [350, 350]
paddle_dx = 0
paddle_dy = 0

ai_paddle_width = 12
ai_paddle_height = 100
ai_paddle_speed = 220
ai_paddle_dy = 0

# --- LESSON: PERSISTENT LEADERBOARDS ---
# We use Python's built-in `json` module to load and save a high-score database
# persistently to a local file. This ensures that leaderboard data remains saved
# even after closing the cabinet.
HIGHSCORES_FILE = "highscores.json"

def load_highscores():
    if os.path.exists(HIGHSCORES_FILE):
        try:
            with open(HIGHSCORES_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return [
        {"name": "CPU", "score": 100},
        {"name": "DUC", "score": 80},
        {"name": "JON", "score": 50},
        {"name": "BOT", "score": 30},
        {"name": "NEW", "score": 10}
    ]

def save_highscores(scores):
    try:
        with open(HIGHSCORES_FILE, "w") as f:
            json.dump(scores, f)
    except:
        pass

highscores = load_highscores()
input_name = ""

def check_high_score_qualification(player_score):
    if len(highscores) < 5:
        return True
    return player_score > highscores[-1]["score"]

def save_high_score(name, player_score):
    global highscores
    highscores.append({"name": name, "score": player_score})
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:5]
    save_highscores(highscores)

# --- LESSON: SCREEN SHAKE VIA VIEWPORT OFFSETS ---
# Visual impact can be heightened by offsetting the drawn frame by a small,
# rapidly changing random vector. Blitting the complete game frames onto a secondary
# surface (`game_surface`) and then blitting that surface to the screen with a
# random offset creates a screen shake effect without altering the physics coordinates.
shake_duration = 0.0
shake_intensity = 0.0

def trigger_shake(duration, intensity):
    global shake_duration, shake_intensity
    shake_duration = duration
    shake_intensity = intensity

# --- LESSON: OBJECT-ORIENTED PYGAME SPRITES ---
# Pygame's `Sprite` class is a base class that packages a graphical Surface (`self.image`)
# and a bounding box (`self.rect`). Grouping sprites together in a `pygame.sprite.Group`
# allows batch rendering, batch updates, and optimized collision calls.
class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, color):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        
        # --- LESSON: PIXEL-PERFECT MASKS ---
        # While a Rect defines the rectangular boundary, a Mask tracks exact filled pixels.
        # Generating a Mask from a Surface with transparency (alpha) lets Pygame verify
        # whether two shapes actually overlapped pixel-by-pixel rather than just their boxes.
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = [0.0, 0.0]
        self.speed = [0.0, 0.0]
        
    def update(self, dt):
        self.pos[0] += self.speed[0] * dt
        self.pos[1] += self.speed[1] * dt
        self.rect.centerx = int(self.pos[0])
        self.rect.centery = int(self.pos[1])

class Paddle(pygame.sprite.Sprite):
    def __init__(self, width, height, color):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, width, height))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = [0.0, 0.0]
        
    def update(self, dt, dx=0, dy=0, speed_x=0, speed_y=0):
        self.pos[0] += dx * speed_x * dt
        self.pos[1] += dy * speed_y * dt
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.color = color

# --- LESSON: PARTICLE SYSTEMS IN GAME ENGINES ---
# A particle system simulates organic visual effects (sparks, smoke, explosions)
# by creating a collection of independent moving shapes (particles) that evolve
# and fade away over time. Each particle is represented as a dictionary storing
# its current physical properties: position, velocity, size, and lifetime.
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.color = color
        self.size = random.uniform(2, 6)
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = [random.uniform(-150, 150), random.uniform(-150, 150)]
        self.lifetime = random.uniform(0.2, 0.5)
        self.max_lifetime = self.lifetime
        self.pos = [float(x), float(y)]
        
    def update(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.rect.center = (int(self.pos[0]), int(self.pos[1]))
        self.lifetime -= dt
        
        # --- LESSON: RENDERING PARTICLES WITH FADE ---
        # To render the particles, we iterate through the active list and draw them on screen.
        # To simulate fading away, we shrink the drawn radius of each particle and shift
        # its color towards the background color (COLOR_BG) based on the particle's remaining lifetime.
        if self.lifetime > 0:
            ratio = self.lifetime / self.max_lifetime
            size = max(1, int(self.size * ratio))
            self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            r = int(COLOR_BG[0] + (self.color[0] - COLOR_BG[0]) * ratio)
            g = int(COLOR_BG[1] + (self.color[1] - COLOR_BG[1]) * ratio)
            b = int(COLOR_BG[2] + (self.color[2] - COLOR_BG[2]) * ratio)
            pygame.draw.circle(self.image, (r, g, b), (size, size), size)

ball = Ball(ball_radius, COLOR_BALL)
paddle = Paddle(paddle_width, paddle_height, COLOR_PADDLE)
ai_paddle = Paddle(ai_paddle_width, ai_paddle_height, COLOR_TEXT)
brick_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

# --- LESSON: BREAKOUT BRICK GRID SETUP ---
# In grid-based games like Breakout, we dynamically generate a layout of bricks.
# Each brick is stored as a dictionary containing a Pygame Rect object (for collision checks)
# and a specific color based on its row, giving the classic retro arcade look.
def init_bricks():
    brick_group.empty()
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
            brick_group.add(Brick(x, y, brick_width, brick_height, color))

def init_game():
    global score, player_score, ai_score, ball_pos, ball_speed
    global paddle_width, paddle_height, paddle_pos, paddle_dx, paddle_dy
    global ai_paddle_pos
    
    particle_group.empty()
    
    if game_mode == "BREAKOUT":
        score = 0
        paddle.width = 120
        paddle.height = 12
        paddle.image = pygame.Surface((paddle.width, paddle.height), pygame.SRCALPHA)
        pygame.draw.rect(paddle.image, COLOR_PADDLE, (0, 0, paddle.width, paddle.height))
        paddle.rect = paddle.image.get_rect()
        paddle.mask = pygame.mask.from_surface(paddle.image)
        paddle.pos = [SCREEN_WIDTH // 2 - paddle.width // 2, SCREEN_HEIGHT - paddle.height - 20]
        paddle.rect.topleft = (int(paddle.pos[0]), int(paddle.pos[1]))
        paddle_dx = 0
        paddle_dy = 0
        
        ball.pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        ball.speed = [150, -200]
        init_bricks()
        
    elif game_mode == "PONG":
        player_score = 0
        ai_score = 0
        paddle.width = 12
        paddle.height = 100
        paddle.image = pygame.Surface((paddle.width, paddle.height), pygame.SRCALPHA)
        pygame.draw.rect(paddle.image, COLOR_PADDLE, (0, 0, paddle.width, paddle.height))
        paddle.rect = paddle.image.get_rect()
        paddle.mask = pygame.mask.from_surface(paddle.image)
        paddle.pos = [20, SCREEN_HEIGHT // 2 - paddle.height // 2]
        paddle.rect.topleft = (int(paddle.pos[0]), int(paddle.pos[1]))
        paddle_dx = 0
        paddle_dy = 0
        
        ai_paddle.pos = [SCREEN_WIDTH - 20 - ai_paddle_width, SCREEN_HEIGHT // 2 - ai_paddle_height // 2]
        ai_paddle.rect.topleft = (int(ai_paddle.pos[0]), int(ai_paddle.pos[1]))
        
        ball.pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        ball.speed = [-250, random.choice([-120, 120])]
        brick_group.empty()

def spawn_particles(x, y, color):
    for _ in range(15):
        particle_group.add(Particle(x, y, color))

running = True
while running:
    
    dt = min(clock.tick(FPS) / 1000.0, 0.1)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "MENU":
                    running = False
                elif state == "ENTER_NAME":
                    pygame.key.stop_text_input()
                    state = "MENU"
                else:
                    state = "MENU"
                
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
                        
            elif state == "ENTER_NAME":
                if event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                elif event.key == pygame.K_RETURN and len(input_name) > 0:
                    save_high_score(input_name, score)
                    pygame.key.stop_text_input()
                    state = "HIGH_SCORES"
                    
            elif state == "GAME_OVER" or state == "WIN" or state == "HIGH_SCORES":
                if event.key == pygame.K_SPACE:
                    init_game()
                    state = "PLAYING"

        elif event.type == pygame.TEXTINPUT:
            # --- LESSON: PYGAME TEXT INPUT ---
            # To accept text entries without bugs, we enable Pygame's built-in text input.
            # This captures keyboard keys (including shifts, accents, layout adjustments)
            # and fires `pygame.TEXTINPUT` events containing the exact character strings.
            if state == "ENTER_NAME":
                if len(input_name) < 3:
                    input_name += event.text.upper()

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
    particle_group.update(dt)
    for p in list(particle_group):
        if p.lifetime <= 0:
            particle_group.remove(p)

    if state == "PLAYING":
        if game_mode == "BREAKOUT":
            paddle.update(dt, dx=paddle_dx, speed_x=paddle_speed[0])

            if paddle.pos[0] < 0:
                paddle.pos[0] = 0
                paddle.rect.x = 0
            elif paddle.pos[0] + paddle.width > SCREEN_WIDTH:
                paddle.pos[0] = SCREEN_WIDTH - paddle_width
                paddle.rect.x = SCREEN_WIDTH - paddle_width

            ball.update(dt)

            if ball.pos[0] - ball_radius <= 0:
                ball.speed[0] = -ball_speed[0]
                ball.pos[0] = ball_radius
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_BORDER)
                trigger_shake(0.1, 3.0)
            elif ball.pos[0] + ball_radius >= SCREEN_WIDTH:
                ball_speed[0] = -ball_speed[0]
                ball_pos[0] = SCREEN_WIDTH - ball_radius
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BORDER)
                trigger_shake(0.1, 3.0)
                
            if ball.pos[1] - ball_radius <= 0:
                ball_speed[1] = -ball_speed[1]
                ball_pos[1] = ball_radius
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BORDER)
                trigger_shake(0.1, 3.0)

            if ball.pos[1] + ball_radius >= SCREEN_HEIGHT:
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BALL)
                trigger_shake(0.3, 10.0)
                if check_high_score_qualification(score):
                    input_name = ""
                    pygame.key.start_text_input()
                    state = "ENTER_NAME"
                else:
                    state = "GAME_OVER"

            # Paddle Collision (Pixel-Perfect using Mask)
            if pygame.sprite.collide_mask(ball, paddle) and ball.speed[1] > 0:
                ball.speed[1] = -ball.speed[1]
                ball.pos[1] = paddle.pos[1] - ball_radius
                
                # --- LESSON: PADDLE ANGLE DEFLECTION ---
                # Instead of a simple vertical bounce, we calculate where the ball strikes
                # the paddle relative to its center. This normalized value (-1.0 at left edge,
                # +1.0 at right edge) is used to deflect the horizontal velocity, giving the player
                # control over directing the ball to target specific bricks.
                paddle_center = paddle.pos[0] + paddle.width / 2
                hit_offset = ball.pos[0] - paddle_center
                normalized_hit = hit_offset / (paddle.width / 2)
                
                ball.speed[0] = normalized_hit * 250
                spawn_particles(ball.pos[0], paddle.pos[1], COLOR_PADDLE)
                trigger_shake(0.12, 4.0)

            # --- LESSON: RECT CLIP COLLISION RESOLUTION ---
            # To make the ball bounce realistically off a brick, we need to know whether
            # it hit the top/bottom edge or the left/right side. Using Pygame's `Rect.clip()`
            # method returns the overlapping area of the collision. If the overlap is wider
            # than it is tall, the collision happened vertically (top/bottom), so we reverse vy.
            # Otherwise, the collision was horizontal (sides), so we reverse vx.
            for brick in list(brick_group):
                if pygame.sprite.collide_mask(ball, brick):
                    overlap = ball.rect.clip(brick.rect)
                    if overlap.width > overlap.height:
                        ball.speed[1] = -ball.speed[1]
                    else:
                        ball.speed[0] = -ball.speed[0]
                    
                    spawn_particles(brick.rect.centerx, brick.rect.centery, brick.color)
                    brick_group.remove(brick)
                    score += 10
                    trigger_shake(0.15, 6.0)
                    break
                    
            if len(brick_group) == 0:
                if check_high_score_qualification(score):
                    input_name = ""
                    pygame.key.start_text_input()
                    state = "ENTER_NAME"
                else:
                    state = "WIN"

        elif game_mode == "PONG":
            paddle.update(dt, dy=paddle_dy, speed_y=paddle_speed[1])
            if paddle.pos[1] < 0:
                paddle.pos[1] = 0
                paddle.rect.y = 0
            elif paddle.pos[1] + paddle.height > SCREEN_HEIGHT:
                paddle.pos[1] = SCREEN_HEIGHT - paddle_height
                paddle.rect.y = SCREEN_HEIGHT - paddle_height

            # --- LESSON: AI OPPONENT LOGIC ---
            # To simulate a computer opponent, the AI paddle compares its vertical center
            # with the ball's vertical position. It moves UP if the ball is above it,
            # and DOWN if the ball is below it. We introduce a small deadzone (+/- 10 pixels)
            # and limit the AI's speed to make it beatable and prevent rapid jittering.
            ai_center = ai_paddle.pos[1] + ai_paddle_height / 2
            if ball.pos[1] < ai_center - 10:
                ai_paddle_dy = -1
            elif ball.pos[1] > ai_center + 10:
                ai_paddle_dy = 1
            else:
                ai_paddle_dy = 0
                
            ai_paddle.update(dt, dy=ai_paddle_dy, speed_y=ai_paddle_speed)
            if ai_paddle.pos[1] < 0:
                ai_paddle.pos[1] = 0
                ai_paddle.rect.y = 0
            elif ai_paddle.pos[1] + ai_paddle_height > SCREEN_HEIGHT:
                ai_paddle.pos[1] = SCREEN_HEIGHT - ai_paddle_height
                ai_paddle.rect.y = SCREEN_HEIGHT - ai_paddle_height

            ball.update(dt)

            if ball.pos[1] - ball_radius <= 0:
                ball.speed[1] = -ball_speed[1]
                ball.pos[1] = ball_radius
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_BORDER)
                trigger_shake(0.1, 3.0)
            elif ball.pos[1] + ball_radius >= SCREEN_HEIGHT:
                ball_speed[1] = -ball_speed[1]
                ball_pos[1] = SCREEN_HEIGHT - ball_radius
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_BORDER)
                trigger_shake(0.1, 3.0)

            # Paddle Collisions (Pixel-Perfect using Mask)
            if pygame.sprite.collide_mask(ball, paddle) and ball.speed[0] < 0:
                ball.speed[0] = -ball.speed[0]
                ball.pos[0] = paddle.pos[0] + paddle.width + ball_radius
                
                hit_offset = ball.pos[1] - (paddle.pos[1] + paddle.height / 2)
                normalized_hit = hit_offset / (paddle.height / 2)
                ball.speed[1] = normalized_hit * 250
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_PADDLE)
                trigger_shake(0.12, 4.0)

            if pygame.sprite.collide_mask(ball, ai_paddle) and ball.speed[0] > 0:
                ball.speed[0] = -ball.speed[0]
                ball.pos[0] = ai_paddle.pos[0] - ball_radius
                
                hit_offset = ball.pos[1] - (ai_paddle.pos[1] + ai_paddle_height / 2)
                normalized_hit = hit_offset / (ai_paddle_height / 2)
                ball.speed[1] = normalized_hit * 250
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_BORDER)
                trigger_shake(0.12, 4.0)

            if ball.pos[0] - ball_radius <= 0:
                spawn_particles(ball.pos[0], ball.pos[1], COLOR_BALL)
                trigger_shake(0.3, 10.0)
                ai_score += 1
                if ai_score >= 5:
                    score = f"{player_score} - {ai_score}"
                    state = "GAME_OVER"
                else:
                    ball.pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball.speed = [250, random.choice([-120, 120])]

            elif ball_pos[0] + ball_radius >= SCREEN_WIDTH:
                spawn_particles(ball_pos[0], ball_pos[1], COLOR_BALL)
                trigger_shake(0.3, 10.0)
                player_score += 1
                if player_score >= 5:
                    score = f"{player_score} - {ai_score}"
                    state = "WIN"
                else:
                    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    ball_speed = [-250, random.choice([-120, 120])]

    if shake_duration > 0:
        shake_duration -= dt
        offset_x = random.randint(-int(shake_intensity), int(shake_intensity))
        offset_y = random.randint(-int(shake_intensity), int(shake_intensity))
        camera_offset = [offset_x, offset_y]
    else:
        camera_offset = [0, 0]

    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_surface.fill(COLOR_BG)

    if state == "MENU":
        title_surface = font_title.render("ARCADE CABINET", True, COLOR_TEXT)
        mode_surface = font_title.render(f"< Mode: {game_mode} >", True, COLOR_PADDLE)
        subtitle_surface = font_subtitle.render("Press UP/DOWN to Switch Mode - Press SPACE to Start - ESC to Quit", True, COLOR_BORDER)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        mode_rect = mode_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        
        game_surface.blit(title_surface, title_rect)
        game_surface.blit(mode_surface, mode_rect)
        game_surface.blit(subtitle_surface, subtitle_rect)

    elif state == "ENTER_NAME":
        title_surface = font_title.render("NEW HIGH SCORE!", True, COLOR_PADDLE)
        name_surface = font_title.render(f"Initials: {input_name}_", True, COLOR_TEXT)
        subtitle_surface = font_subtitle.render("Type 3 letters & press ENTER to save", True, COLOR_BORDER)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        
        game_surface.blit(title_surface, title_rect)
        game_surface.blit(name_surface, name_rect)
        game_surface.blit(subtitle_surface, subtitle_rect)

    elif state == "HIGH_SCORES":
        title_surface = font_title.render("LEADERBOARD (BREAKOUT)", True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
        game_surface.blit(title_surface, title_rect)
        
        for idx, entry in enumerate(highscores):
            entry_text = f"{idx + 1}. {entry['name']}  ---  {entry['score']}"
            entry_surface = font_title.render(entry_text, True, COLOR_PADDLE if idx == 0 else COLOR_TEXT)
            entry_rect = entry_surface.get_rect(center=(SCREEN_WIDTH // 2, 160 + idx * 50))
            game_surface.blit(entry_surface, entry_rect)
            
        subtitle_surface = font_subtitle.render("Press SPACE or ESC to return to Menu", True, COLOR_BORDER)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        game_surface.blit(subtitle_surface, subtitle_rect)

    elif state == "PLAYING":
        if game_mode == "BREAKOUT":
            score_surface = font_title.render(f"Score: {score}", True, COLOR_TEXT)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            game_surface.blit(score_surface, score_rect)
            
            instructions_surface = font_subtitle.render("Move paddle with Left/Right Keys - Press ESC for Menu", True, COLOR_BORDER)
            instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            game_surface.blit(instructions_surface, instructions_rect)

            game_surface.blit(ball.image, ball.rect)
            game_surface.blit(paddle.image, paddle.rect)
            brick_group.draw(game_surface)
            particle_group.draw(game_surface)
            
        elif game_mode == "PONG":
            score_surface = font_title.render(f"{player_score}   {ai_score}", True, COLOR_TEXT)
            score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
            game_surface.blit(score_surface, score_rect)
            
            for y in range(0, SCREEN_HEIGHT, 30):
                pygame.draw.rect(game_surface, (60, 60, 80), (SCREEN_WIDTH // 2 - 2, y, 4, 15))
            
            instructions_surface = font_subtitle.render("Move paddle with Up/Down Keys - Press ESC for Menu", True, COLOR_BORDER)
            instructions_rect = instructions_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            game_surface.blit(instructions_surface, instructions_rect)

            game_surface.blit(ball.image, ball.rect)
            game_surface.blit(paddle.image, paddle.rect)
            game_surface.blit(ai_paddle.image, ai_paddle.rect)
            particle_group.draw(game_surface)

    elif state == "GAME_OVER":
        title_surface = font_title.render("GAME OVER", True, COLOR_BALL)
        
        if game_mode == "BREAKOUT":
            sub_text = f"Final Score: {score} | Press SPACE to Restart - ESC for Menu"
        else:
            sub_text = f"Final Score: {score} (AI Wins) | Press SPACE to Restart - ESC for Menu"
            
        subtitle_surface = font_subtitle.render(sub_text, True, COLOR_TEXT)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        game_surface.blit(title_surface, title_rect)
        game_surface.blit(subtitle_surface, subtitle_rect)

    elif state == "WIN":
        title_surface = font_title.render("YOU WIN!", True, COLOR_PADDLE)
        
        if game_mode == "BREAKOUT":
            sub_text = f"Final Score: {score} | Press SPACE to Play Again - ESC for Menu"
        else:
            sub_text = f"Final Score: {score} (You Beat AI!) | Press SPACE to Play Again - ESC for Menu"
            
        subtitle_surface = font_subtitle.render(sub_text, True, COLOR_TEXT)
        
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        
        game_surface.blit(title_surface, title_rect)
        game_surface.blit(subtitle_surface, subtitle_rect)

    screen.fill((0, 0, 0))
    screen.blit(game_surface, camera_offset)
    pygame.display.flip()

pygame.quit()
sys.exit()
