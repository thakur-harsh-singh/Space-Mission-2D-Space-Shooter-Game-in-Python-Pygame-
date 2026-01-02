import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

# ================== WINDOW ==================
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption("Space Mission")
clock = pygame.time.Clock()
WIDTH, HEIGHT = screen.get_size()

# ================== PATHS ==================
BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")

# ================== LOAD RAW ASSETS ==================
bg_raw = pygame.image.load(os.path.join(ASSETS, "backgrounds", "space_bg.jpg")).convert()
logo_raw = pygame.image.load(os.path.join(ASSETS, "sprites", "logo.png")).convert_alpha()
player_raw = pygame.image.load(os.path.join(ASSETS, "sprites", "player.png")).convert_alpha()
enemy_raw = pygame.image.load(os.path.join(ASSETS, "sprites", "Enemy1.png")).convert_alpha()
bullet_raw = pygame.image.load(os.path.join(ASSETS, "sprites", "player_bullet.png")).convert_alpha()
boss_bullet_raw = pygame.image.load(os.path.join(ASSETS, "sprites", "boss_big_bullet.png")).convert_alpha()

shoot_sound = pygame.mixer.Sound(os.path.join(ASSETS, "sounds", "shoot.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(ASSETS, "sounds", "explosion.wav"))

# ================== FONTS ==================
def load_fonts():
    return (
        pygame.font.SysFont("arial", int(HEIGHT * 0.03)),
        pygame.font.SysFont("arial", int(HEIGHT * 0.06)),
        pygame.font.SysFont("arial", int(HEIGHT * 0.09))
    )

FONT, BIG_FONT, TITLE_FONT = load_fonts()

# ================== SCALE ASSETS ==================
def scale_assets():
    global background, logo, player_img, enemy_img, bullet_img, boss_img, boss_bullet_img

    background = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
    logo = pygame.transform.scale(logo_raw, (int(WIDTH * 0.25), int(HEIGHT * 0.25)))

    player_img = pygame.transform.scale(player_raw, (int(WIDTH * 0.05), int(HEIGHT * 0.08)))
    enemy_img = pygame.transform.scale(enemy_raw, (int(WIDTH * 0.07), int(HEIGHT * 0.1)))
    bullet_img = pygame.transform.scale(bullet_raw, (int(WIDTH * 0.015), int(HEIGHT * 0.04)))

    boss_img = pygame.transform.scale(enemy_img, (int(WIDTH * 0.18), int(HEIGHT * 0.25)))
    boss_bullet_img = pygame.transform.scale(
        boss_bullet_raw, (int(WIDTH * 0.03), int(HEIGHT * 0.06))
    )

scale_assets()

# ================== GAME STATES ==================
SPLASH, PLAYING, PAUSED, GAME_OVER = "SPLASH", "PLAYING", "PAUSED", "GAME_OVER"
game_state = SPLASH

# ================== VARIABLES ==================
bullets = []
enemies = []
enemy_bullets = []

enemy_speed = int(HEIGHT * 0.005)
spawn_delay = 100
spawn_timer = 0

player_health = 5
score = 0

boss_active = False
boss_spawn_score = 10
boss_max_health = 30
boss_health = boss_max_health
boss_speed = 4

enemy_bullet_speed = 10
enemy_fire_delay = 45
enemy_fire_timer = 0

# ================== RESET GAME ==================
def reset_game():
    global player_rect, bullets, enemies, enemy_bullets
    global score, player_health, boss_active, boss_rect, boss_health
    global spawn_timer, enemy_fire_timer

    player_rect = player_img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 30))
    bullets.clear()
    enemies.clear()
    enemy_bullets.clear()

    score = 0
    player_health = 5
    boss_active = False
    boss_health = boss_max_health

    spawn_timer = 0
    enemy_fire_timer = 0

reset_game()

# ================== BUTTON ==================
def button(text, x, y, w, h):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    rect = pygame.Rect(x, y, w, h)

    pygame.draw.rect(screen, (60, 60, 180), rect, border_radius=12)
    label = FONT.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))

    if rect.collidepoint(mouse) and click:
        pygame.time.delay(200)
        return True
    return False

# ================== MAIN LOOP ==================
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            FONT, BIG_FONT, TITLE_FONT = load_fonts()
            scale_assets()
            reset_game()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = PAUSED if game_state == PLAYING else PLAYING

            if event.key == pygame.K_SPACE and game_state == PLAYING:
                bullets.append(bullet_img.get_rect(midbottom=player_rect.midtop))
                shoot_sound.play()

    # ================= SPLASH =================
    if game_state == SPLASH:
        screen.blit(background, (0, 0))
        screen.blit(logo, logo.get_rect(center=(WIDTH // 2, HEIGHT * 0.25)))

        title = TITLE_FONT.render("SPACE MISSION", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT * 0.5)))

        if button("PLAY", WIDTH // 2 - 150, int(HEIGHT * 0.65), 300, 60):
            reset_game()
            game_state = PLAYING

        if button("QUIT", WIDTH // 2 - 150, int(HEIGHT * 0.75), 300, 60):
            running = False

    # ================= PAUSED =================
    elif game_state == PAUSED:
        screen.blit(background, (0, 0))
        text = BIG_FONT.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT * 0.4)))

        if button("RESUME", WIDTH // 2 - 150, int(HEIGHT * 0.5), 300, 60):
            game_state = PLAYING

        if button("NEW GAME", WIDTH // 2 - 150, int(HEIGHT * 0.6), 300, 60):
            reset_game()
            game_state = PLAYING

        if button("QUIT", WIDTH // 2 - 150, int(HEIGHT * 0.7), 300, 60):
            running = False

    # ================= GAME OVER =================
    elif game_state == GAME_OVER:
        screen.blit(background, (0, 0))

        lose = BIG_FONT.render("YOU LOSE!", True, (255, 60, 60))
        score_text = FONT.render(f"Your Score: {score}", True, (255, 255, 255))

        screen.blit(lose, lose.get_rect(center=(WIDTH // 2, HEIGHT * 0.4)))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, HEIGHT * 0.5)))

        if button("NEW GAME", WIDTH // 2 - 150, int(HEIGHT * 0.6), 300, 60):
            reset_game()
            game_state = PLAYING

        if button("QUIT", WIDTH // 2 - 150, int(HEIGHT * 0.7), 300, 60):
            running = False

    # ================= PLAYING =================
    elif game_state == PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_rect.x -= 10
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_rect.x += 10
        player_rect.x = max(0, min(WIDTH - player_rect.width, player_rect.x))

        for b in bullets[:]:
            b.y -= 15
            if b.bottom < 0:
                bullets.remove(b)

        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            spawn_timer = 0
            enemies.append(enemy_img.get_rect(
                midtop=(random.randint(50, WIDTH - 50), -60)
            ))

        for e in enemies[:]:
            e.y += enemy_speed
            if e.top > HEIGHT:
                enemies.remove(e)
                player_health -= 1

            for b in bullets[:]:
                if e.colliderect(b):
                    enemies.remove(e)
                    bullets.remove(b)
                    explosion_sound.play()
                    score += 1
                    break

        if score >= boss_spawn_score and not boss_active:
            boss_rect = boss_img.get_rect(midtop=(WIDTH // 2, 20))
            boss_active = True
            boss_health = boss_max_health

        if boss_active:
            boss_rect.x += boss_speed
            if boss_rect.left <= 0 or boss_rect.right >= WIDTH:
                boss_speed *= -1

            enemy_fire_timer += 1
            if enemy_fire_timer >= enemy_fire_delay:
                enemy_fire_timer = 0
                enemy_bullets.append(
                    boss_bullet_img.get_rect(midtop=(boss_rect.centerx, boss_rect.bottom))
                )

        for eb in enemy_bullets[:]:
            eb.y += enemy_bullet_speed
            if eb.top > HEIGHT:
                enemy_bullets.remove(eb)
            elif eb.colliderect(player_rect):
                enemy_bullets.remove(eb)
                player_health -= 1

        if boss_active:
            for b in bullets[:]:
                if boss_rect.colliderect(b):
                    bullets.remove(b)
                    boss_health -= 1
                    explosion_sound.play()
                    if boss_health <= 0:
                        boss_active = False
                        enemy_bullets.clear()
                        score += 10

        screen.blit(background, (0, 0))
        screen.blit(player_img, player_rect)

        for b in bullets:
            screen.blit(bullet_img, b)

        for e in enemies:
            screen.blit(enemy_img, e)

        for eb in enemy_bullets:
            screen.blit(boss_bullet_img, eb)

        if boss_active:
            screen.blit(boss_img, boss_rect)
            ratio = boss_health / boss_max_health
            pygame.draw.rect(screen, (255, 0, 0),
                             (boss_rect.x, boss_rect.y - 15, boss_rect.width, 8))
            pygame.draw.rect(screen, (0, 255, 0),
                             (boss_rect.x, boss_rect.y - 15, boss_rect.width * ratio, 8))

        screen.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (20, 20))
        screen.blit(FONT.render(f"Health: {player_health}", True, (255, 255, 255)), (20, 60))

        if player_health <= 0:
            game_state = GAME_OVER

    pygame.display.update()

pygame.quit()
sys.exit()
