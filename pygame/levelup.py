import math
import random
import pygame
import os
from pygame import mixer

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# Font setup
menu_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
score_font = pygame.font.Font(None, 32)
over_font = pygame.font.Font(None, 64)

# High score file
HIGH_SCORE_FILE = "space_invaders_highscore.txt"

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))

def show_message(screen, font, message, y_pos, color=(255, 255, 255)):
    text = font.render(message, True, color)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
    pygame.display.update()
    return text.get_rect(topleft=(WIDTH//2 - text.get_width()//2, y_pos))

# Sound selection menu
sound_enabled = None
while sound_enabled is None:
    screen.fill((0, 0, 0))
    
    title_rect = show_message(screen, menu_font, "SPACE INVADERS", 150)
    sound_rect = show_message(screen, small_font, "Enable Sound? (Y/N)", 300)
    controls_rect = show_message(screen, small_font, "Controls: Arrows to Move, Space to Shoot", 400, (200, 200, 200))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                sound_enabled = True
            elif event.key == pygame.K_n:
                sound_enabled = False

# Load assets
try:
    background = pygame.image.load('background.png')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((0, 0, 20))

# Sound setup
if sound_enabled:
    try:
        mixer.music.load("background.wav")
        mixer.music.set_volume(0.5)
        mixer.music.play(-1)
        laser_sound = mixer.Sound("laser.wav")
        laser_sound.set_volume(0.7)
        explosion_sound = mixer.Sound("explosion.wav")
        explosion_sound.set_volume(0.7)
        level_up_sound = mixer.Sound("level_up.wav") if os.path.exists("level_up.wav") else None
    except:
        sound_enabled = False

# Player setup
try:
    playerImg = pygame.image.load('player.png')
except:
    playerImg = pygame.Surface((50, 50))
    playerImg.fill((0, 255, 0))

playerX = 370
playerY = 480
playerX_change = 0
player_speed = 5

# Enemy setup
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6

for i in range(num_of_enemies):
    try:
        img = pygame.image.load('enemy.png')
    except:
        img = pygame.Surface((40, 40))
        img.fill((255, 0, 0))
    enemyImg.append(img)
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(4)
    enemyY_change.append(40)

# Bullet setup
try:
    bulletImg = pygame.image.load('bullet.png')
except:
    bulletImg = pygame.Surface((5, 15))
    bulletImg.fill((255, 255, 255))

bulletX = 0
bulletY = 480
bullet_speed = 10
bullet_state = "ready"  # "ready" or "fire"

# Game variables
score_value = 0
high_score = load_high_score()
level = 1
level_up_threshold = 5  # Points needed to level up
enemy_speed_increase = 0.5  # Speed increase per level
textX = 10
textY = 10

# Game functions
def show_game_info():
    score = score_font.render(f"Score: {score_value}", True, (255, 255, 255))
    screen.blit(score, (textX, textY))
    
    high_score_text = score_font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (textX, textY + 30))
    
    level_text = score_font.render(f"Level: {level}", True, (255, 255, 255))
    screen.blit(level_text, (textX, textY + 60))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
    
    final_score = small_font.render(f"Final Score: {score_value}", True, (200, 200, 255))
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 20))
    
    restart_text = small_font.render("Press R to Restart or Q to Quit", True, (200, 200, 200))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    return distance < 27

def check_level_up():
    global level, level_up_threshold, enemyX_change, num_of_enemies
    
    # Calculate required points for next level (increases with each level)
    required_points = level_up_threshold * level
    
    if score_value >= required_points:
        level += 1
        if sound_enabled and level_up_sound:
            level_up_sound.play()
        
        # Increase enemy speed
        for i in range(num_of_enemies):
            enemyX_change[i] += enemy_speed_increase if enemyX_change[i] > 0 else -enemy_speed_increase
        
        # Occasionally add a new enemy (max 12 enemies)
        if num_of_enemies < 12 and level % 2 == 0:
            try:
                img = pygame.image.load('enemy.png')
            except:
                img = pygame.Surface((40, 40))
                img.fill((255, 0, 0))
            enemyImg.append(img)
            enemyX.append(random.randint(0, 736))
            enemyY.append(random.randint(50, 150))
            enemyX_change.append(4 + (level * enemy_speed_increase))
            enemyY_change.append(40)
            num_of_enemies += 1

# Game loop
running = True
game_active = True

while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -player_speed
            if event.key == pygame.K_RIGHT:
                playerX_change = player_speed
            if event.key == pygame.K_SPACE and game_active:
                if bullet_state == "ready":
                    if sound_enabled:
                        laser_sound.play()
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
            
            # Restart game
            if not game_active and event.key == pygame.K_r:
                # Reset game state
                playerX = 370
                playerY = 480
                playerX_change = 0
                bullet_state = "ready"
                score_value = 0
                level = 1
                game_active = True
                
                # Reset enemies
                enemyX = []
                enemyY = []
                enemyX_change = []
                enemyY_change = []
                num_of_enemies = 6
                for i in range(num_of_enemies):
                    enemyX.append(random.randint(0, 736))
                    enemyY.append(random.randint(50, 150))
                    enemyX_change.append(4)
                    enemyY_change.append(40)
            
            # Quit game
            if not game_active and event.key == pygame.K_q:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    if game_active:
        # Player movement
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= WIDTH - 64:
            playerX = WIDTH - 64

        # Enemy movement
        for i in range(num_of_enemies):
            # Game Over condition
            if enemyY[i] > 440:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000  # Move all enemies off screen
                game_active = False
                # Update high score if needed
                if score_value > high_score:
                    high_score = score_value
                    save_high_score(high_score)
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = 4 + (level * enemy_speed_increase)
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= WIDTH - 64:
                enemyX_change[i] = -4 - (level * enemy_speed_increase)
                enemyY[i] += enemyY_change[i]

            # Collision detection
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                if sound_enabled:
                    explosion_sound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, WIDTH - 64)
                enemyY[i] = random.randint(50, 150)
                
                # Check for level up
                check_level_up()

            enemy(enemyX[i], enemyY[i], i)

        # Bullet movement
        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bullet_speed
            if bulletY <= 0:
                bullet_state = "ready"
                bulletY = 480

        player(playerX, playerY)
        show_game_info()
    else:
        game_over_text()

    pygame.display.update()

pygame.quit()