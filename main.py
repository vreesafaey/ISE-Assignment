import pygame
from pygame import mixer
from LEVEL1 import Fighter  # Assuming Fighter is defined in LEVEL1.py

mixer.init()
pygame.init()

# Game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brawler")

# Framerate
clock = pygame.time.Clock()
FPS = 60

# Colours
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# Game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_OVER_COOLDOWN = 2000
current_level = 1
MAX_LEVEL = 3

# Fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

# Sounds
pygame.mixer.music.load("assets/audio/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

# Backgrounds
bg_image1 = pygame.image.load("assets/images/background/background1.jpg").convert_alpha()
bg_image2 = pygame.image.load("assets/images/background/background2.jpg").convert_alpha()
bg_image3 = pygame.image.load("assets/images/background/background3.jpg").convert_alpha()

# Spritesheets
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()

# Victory image
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

# Animation steps
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

# Fonts
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

# Draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_button(text, font, color, x, y, width, height):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)
    
    # Highlight if mouse over
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (100, 100, 100), button_rect)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, (50, 50, 50), button_rect)
        
    # Draw border and text
    pygame.draw.rect(screen, color, button_rect, 2)
    draw_text(text, font, color, x + 10, y + 10)
    return False


# Draw background based on level
def draw_bg():
    if current_level == 1:
        bg = bg_image1
    elif current_level == 2:
        bg = bg_image2
    elif current_level == 3:
        bg = bg_image3
    else:
        bg = bg_image1
    scaled_bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

# Draw health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

# Create fighters
def create_fighters():
    f1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    f2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    return f1, f2

fighter_1, fighter_2 = create_fighters()


# Game loop
run = True
game_over = False
winner = None  # Track the winner after Level 3

while run:
    clock.tick(FPS)

    draw_bg()


    # Show health and scores
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
    draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

    # Countdown logic
    if intro_count <= 0 and not game_over:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
    elif not game_over:
        draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # Update fighters
    fighter_1.update()
    fighter_2.update()
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # Check for round over
    if not round_over and not game_over:
        if not fighter_1.alive:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            if current_level == MAX_LEVEL:
                winner = 2
                game_over = True
                game_over_time = pygame.time.get_ticks()
        elif not fighter_2.alive:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            if current_level == MAX_LEVEL:
                winner = 1
                game_over = True
                game_over_time = pygame.time.get_ticks()

    # Handle game over and victory UI
    elif game_over:
        victory_text = f"PLAYER {winner} WINS!"
        draw_text(victory_text, count_font, RED, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 3)

        play_again = draw_button("Play Again", score_font, RED, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 200, 50)
        exit_game = draw_button("Exit", score_font, RED, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 200, 50)

        if play_again:
            score = [0, 0]
            current_level = 1
            intro_count = 3
            round_over = False
            game_over = False
            fighter_1, fighter_2 = create_fighters()
            pygame.mixer.music.load("assets/audio/music.mp3")
            pygame.mixer.music.play(-1, 0.0, 5000)

        elif exit_game:
            run = False

    # If round over but game not finished
    elif round_over:
        screen.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3

            # LEVEL TRANSITION
            current_level += 1
            if current_level > MAX_LEVEL:
                current_level = MAX_LEVEL
                game_over = True
                game_over_time = pygame.time.get_ticks()
            else:
                pygame.mixer.music.load("assets/audio/music.mp3")
                pygame.mixer.music.play(-1, 0.0, 5000)
                fighter_1, fighter_2 = create_fighters()

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
