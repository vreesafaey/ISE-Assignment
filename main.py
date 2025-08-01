import pygame
from pygame import mixer
from LEVEL1 import Fighter as Fighter1  # Fighter for LEVEL1
from LEVEL2 import Fighter as Fighter2  # Fighter for LEVEL2
from PIL import Image

mixer.init()
pygame.init()

# Game window
SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fantasy Duel")

# Framerate
clock = pygame.time.Clock()
FPS = 60

# Colours
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)

# Game states
MAIN_MENU = 0
PLAYING = 1
EXIT_SCREEN = 2

# Game variables
game_state = MAIN_MENU
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_OVER_COOLDOWN = 2000
current_level = 1
selected_level = 1
MAX_LEVEL = 2
games_completed = 0
MAX_GAMES = 3

Samurai_Size = 128
Samurai_Scale = 2.55
Samurai_Offset = [55, 30]
Samurai_Data = [Samurai_Size, Samurai_Scale, Samurai_Offset]
Magician_Size = 128
Magician_Scale = 3
Magician_Offset = [55, 45]
Magician_Data = [Magician_Size, Magician_Scale, Magician_Offset]

# Sounds
game_music = pygame.mixer.Sound("assets/audio/battle-fighting-warrior-drums-372078.mp3")
game_music.set_volume(0.5)
game_music.play(-1)

try:
    button_sound = pygame.mixer.Sound("assets/audio/button-305770.mp3")
    button_sound.set_volume(0.5)
except:
    button_sound = None
    print("Button sound file not found")

Samurai_fx = pygame.mixer.Sound("assets/audio/Samurai_sound/sword-blade-slicing-flesh-352708.mp3")
Samurai_fx.set_volume(0.1)
Samurai_attack_sound1 = pygame.mixer.Sound("assets/audio/Samurai_sound/sword-blade-slicing-flesh-352708.mp3")
Samurai_attack_sound1.set_volume(0.1)

bg_frames = []
bg_frame_index = 0
bg_animation_speed = 100
bg_last_update = pygame.time.get_ticks()
round_start_time = None
debuff_threshold = 10000
debuff_activated = False
debuff_warning_shown = False

def load_gif_frames(gif_path, brightness_factor=0.8):
    frames = []
    try:
        gif = Image.open(gif_path)
        frame_count = 0
        while True:
            try:
                frame = gif.copy()
                frame = frame.convert('RGBA')
                pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                scaled_frame = pygame.transform.scale(pygame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                if brightness_factor != 1.0:
                    scaled_frame = adjust_brightness(scaled_frame, brightness_factor)
                frames.append(scaled_frame)
                frame_count += 1
                gif.seek(frame_count)
            except EOFError:
                break
    except Exception as e:
        print(f"Error loading GIF: {e}")
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((50, 50, 100))
        frames.append(fallback)
    return frames

def adjust_brightness(surface, brightness_factor):
    if brightness_factor < 1.0:
        overlay = pygame.Surface(surface.get_size()).convert_alpha()
        brightness_value = int(255 * brightness_factor)
        overlay.fill((brightness_value, brightness_value, brightness_value, 255))
        result = surface.copy()
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        return result
    elif brightness_factor > 1.0:
        overlay = pygame.Surface(surface.get_size()).convert_alpha()
        brightness_value = int(255 * (brightness_factor - 1.0))
        overlay.fill((brightness_value, brightness_value, brightness_value, 255))
        result = surface.copy()
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        return result
    else:
        return surface

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_centered_text(text, font, text_col, y):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect()
    text_rect.centerx = SCREEN_WIDTH // 2
    screen.blit(img, (text_rect.x, y))

def draw_button(text, font, color, x, y, width, height):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)
    global last_hovered_button
    if not hasattr(draw_button, 'last_hovered_button'):
        draw_button.last_hovered_button = None
    if button_rect.collidepoint(mouse_pos):
        if draw_button.last_hovered_button != button_rect and button_sound:
            try:
                hover_sound = pygame.mixer.Sound("assets/audio/button_hover.wav")
                hover_sound.set_volume(0.2)
                hover_sound.play()
            except:
                pass
        draw_button.last_hovered_button = button_rect
        pygame.draw.rect(screen, (100, 100, 100), button_rect)
        if click[0] == 1:
            if button_sound:
                button_sound.play()
            return True
    else:
        if draw_button.last_hovered_button == button_rect:
            draw_button.last_hovered_button = None
        pygame.draw.rect(screen, (50, 50, 50), button_rect)
    pygame.draw.rect(screen, color, button_rect, 2)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return False

def draw_main_menu():
    draw_menu_bg()
    draw_centered_text("--FANTASY DUEL--", title_font, BLACK, 109)
    draw_centered_text("--FANTASY DUEL--", title_font, RED, 100)
    draw_centered_text("Ultimate Fighting Championship", subtitle_font, BLACK, 182)
    draw_centered_text("Ultimate Fighting Championship", subtitle_font, WHITE, 180)
    button_width = 200
    button_height = 80
    button_spacing = 50
    start_x = SCREEN_WIDTH // 2 - (2 * button_width + button_spacing) // 2
    stage1_btn = draw_button("STAGE 1", menu_font, BLUE, start_x, 280, button_width, button_height)
    stage2_btn = draw_button("STAGE 2", menu_font, BLUE, start_x + button_width + button_spacing, 280, button_width, button_height)
    exit_btn = draw_button("EXIT", menu_font, WHITE, SCREEN_WIDTH // 2 - 100, 400, 200, 50)
    return stage1_btn, stage2_btn, exit_btn

def draw_exit_screen():
    screen.fill(BLACK)
    draw_centered_text("CONGRATULATIONS!", title_font, YELLOW, 150)
    draw_centered_text(f"You completed {games_completed} games!", subtitle_font, WHITE, 220)
    draw_centered_text(f"Player 1 Total Wins: {score[0]}", menu_font, RED, 300)
    draw_centered_text(f"Player 2 Total Wins: {score[1]}", menu_font, RED, 340)
    if score[0] > score[1]:
        winner_text = "Player 1 is the Ultimate Champion!"
        winner_color = RED
    elif score[1] > score[0]:
        winner_text = "Player 2 is the Ultimate Champion!"
        winner_color = RED
    else:
        winner_text = "It's a tie! Both players are champions!"
        winner_color = YELLOW
    draw_centered_text(winner_text, subtitle_font, winner_color, 400)
    return_menu = draw_button("RETURN TO MAIN MENU", menu_font, WHITE, SCREEN_WIDTH // 2 - 200, 480, 400, 60)
    return return_menu

def draw_menu_bg():
    try:
        scaled_bg = pygame.transform.scale(menu_bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    except:
        try:
            global menu_bg_frame_index, menu_bg_last_update
            current_time = pygame.time.get_ticks()
            if current_time - menu_bg_last_update > bg_animation_speed:
                menu_bg_frame_index = (menu_bg_frame_index + 1) % len(menu_bg_frames)
                menu_bg_last_update = current_time
            screen.blit(menu_bg_frames[menu_bg_frame_index], (0, 0))
        except:
            draw_gradient_background()

def draw_gradient_background():
    for y in range(SCREEN_HEIGHT):
        color_ratio = y / SCREEN_HEIGHT
        r = int(20 * (1 - color_ratio))
        g = int(30 * (1 - color_ratio))
        b = int(80 * (1 - color_ratio))
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_bg():
    global bg_frame_index, bg_last_update
    if current_level == 1:
        current_time = pygame.time.get_ticks()
        if current_time - bg_last_update > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames_level1)
            bg_last_update = current_time
        screen.blit(bg_frames_level1[bg_frame_index], (0, 0))
    elif current_level == 2:
        scaled_bg = pygame.transform.scale(bg_image2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))
    else:
        screen.blit(bg_frames_level1[0], (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 504, 34))
    pygame.draw.rect(screen, RED, (x, y, 500, 30))
    pygame.draw.rect(screen, GREEN, (x, y, 500 * ratio / 1.5, 30))

def create_fighters():
    if current_level == 1:
        f1 = Fighter1(1, 200, 310, False, Samurai_Data, Samurai_sheet, Samurai_Animation_Steps, Samurai_fx)
        f2 = Fighter1(2, 1000, 310, True, Magician_Data, Magician_sheet, Magician_Animation_Steps, Samurai_fx)
    else:  # current_level == 2
        f1 = Fighter2(1, 200, 310, False, Samurai_Data, Samurai_sheet, Samurai_Animation_Steps, Samurai_fx)
        f2 = Fighter2(2, 1000, 310, True, Magician_Data, Magician_sheet, Magician_Animation_Steps, Samurai_fx)
    return f1, f2

def check_debuff_timer():
    global round_start_time, debuff_activated, debuff_warning_shown
    if intro_count <= 0 and round_start_time is None and not round_over and game_state == PLAYING:
        round_start_time = pygame.time.get_ticks()
        print("Round timer started!")
    if round_start_time is not None and not round_over and game_state == PLAYING:
        elapsed_time = pygame.time.get_ticks() - round_start_time
        if elapsed_time >= 8000 and not debuff_warning_shown:
            debuff_warning_shown = True
            print("Warning: Debuff activating in 2 seconds!")
        if elapsed_time >= debuff_threshold and not debuff_activated:
            debuff_activated = True
            fighter_1.activate_debuff()
            fighter_2.activate_debuff()
            print("DEBUFF ACTIVATED! Both players losing 2 HP per second!")

def reset_timer():
    global round_start_time, debuff_activated, debuff_warning_shown
    round_start_time = None
    debuff_activated = False
    debuff_warning_shown = False

def reset_game():
    global intro_count, round_over, bg_frame_index, fighter_1, fighter_2
    intro_count = 3
    round_over = False
    bg_frame_index = 0
    reset_timer()
    fighter_1, fighter_2 = create_fighters()

def get_health_color(health, max_health):
    ratio = health / max_health
    if ratio > 0.6:
        return (0, 255, 0)
    elif ratio > 0.3:
        return (255, 255, 0)
    else:
        return (255, 0, 0)

# Background images and variables
bg_frames_level1 = load_gif_frames("assets/images/background/arenaOption4.gif")
bg_image2 = pygame.image.load("assets/images/background/background2.jpg").convert_alpha()
try:
    menu_bg_image = pygame.image.load("assets/images/background/background1.jpg").convert_alpha()
    menu_bg_frames = None
    print("Menu background loaded successfully: background1.jpg")
except:
    try:
        menu_bg_frames = load_gif_frames("assets/images/background/menu_background.gif", brightness_factor=0.6)
        menu_bg_image = None
    except:
        menu_bg_frames = None
        menu_bg_image = None
        print("No menu background found, using gradient fallback")

# Spritesheets
Samurai_sheet = pygame.image.load("assets/images/Samurai/Sprites/Samurai_Spritelist.png").convert_alpha()
Magician_sheet = pygame.image.load("assets/images/Magician/Sprites/Wanderer_Magican_Spritelist.png").convert_alpha()
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

# Animation steps
Samurai_Animation_Steps = [6, 8, 8, 12, 6, 4, 3, 2, 2, 3]
Magician_Animation_Steps = [8, 7, 8, 7, 9, 16, 11, 8, 2, 4]

# Fonts
title_font = pygame.font.Font("assets/fonts/VTFRedzone-Classic.ttf", 80)
subtitle_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
menu_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
count_font = pygame.font.Font("assets/fonts/VTFRedzone-Classic.ttf", 120)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
stage_font = pygame.font.Font("assets/fonts/turok.ttf", 60)
timer_font = pygame.font.Font("assets/fonts/turok.ttf", 20)
debuff_font = pygame.font.Font("assets/fonts/turok.ttf", 24)

# Initialize fighters
fighter_1, fighter_2 = create_fighters()

# Music management
current_music = None

def play_menu_music():
    global current_music
    if current_music != "menu":
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/audio/menu_music.mp3")
            pygame.mixer.music.play(-1)
            current_music = "menu"
        except:
            pass

def play_game_music():
    global current_music
    if current_music != "game":
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/audio/game_music.mp3")
            pygame.mixer.music.play(-1)
            current_music = "game"
        except:
            pass

# Game loop
run = True
while run:
    clock.tick(FPS)
    if game_state == MAIN_MENU:
        play_menu_music()
        stage1_btn, stage2_btn, exit_btn = draw_main_menu()
        if stage1_btn:
            selected_level = 1
            current_level = 1
            score = [0, 0]
            games_completed = 0
            game_state = PLAYING
            play_game_music()
            reset_game()
        elif stage2_btn:
            selected_level = 2
            current_level = 2
            score = [0, 0]
            games_completed = 0
            game_state = PLAYING
            play_game_music()
            reset_game()
        elif exit_btn:
            run = False
    elif game_state == PLAYING:
        draw_bg()
        health_font = pygame.font.Font("assets/fonts/turok.ttf", 20)
        p1_health_color = get_health_color(fighter_1.health, 150)
        p2_health_color = get_health_color(fighter_2.health, 150)
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 820, 20)
        draw_text(f"Level {current_level}", stage_font, WHITE, 585, 8)
        draw_text("P1: " + str(score[0]), score_font, RED, 20, 55)
        draw_text("P2: " + str(score[1]), score_font, RED, 820, 55)
        draw_text(f"HP: {fighter_1.health}/150", health_font, p1_health_color, 430, 52)
        draw_text(f"HP: {fighter_2.health}/150", health_font, p2_health_color, 1230, 52)
        draw_text(f"Games: {games_completed}/{MAX_GAMES}", score_font, WHITE, SCREEN_WIDTH // 2 - 50, 90)
        check_debuff_timer()
        if round_start_time is not None and not round_over and game_state == PLAYING:
            elapsed_time = (pygame.time.get_ticks() - round_start_time) // 1000
            time_remaining = max(0, 10 - elapsed_time)
            if debuff_activated:
                draw_text("DEBUFF ACTIVE!", debuff_font, RED, SCREEN_WIDTH // 2 - 70, 100)
            elif debuff_warning_shown:
                draw_text(f"DEBUFF IN: {time_remaining}", debuff_font, YELLOW, SCREEN_WIDTH // 2 - 70, 100)
            draw_text(f"Time: {elapsed_time}s", timer_font, WHITE, SCREEN_WIDTH // 2 - 35, 70)
        if intro_count <= 0:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        else:
            draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2 - 30, SCREEN_HEIGHT / 3 + 20)
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()
        fighter_1.update()
        fighter_2.update()
        fighter_1.check_projectile_collision(fighter_2)
        fighter_2.check_projectile_collision(fighter_1)
        fighter_1.draw(screen)
        fighter_2.draw(screen)
        if not round_over:
            if not fighter_1.alive:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
                reset_timer()
            elif not fighter_2.alive:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
                reset_timer()
        if round_over:
            screen.blit(victory_img, (360, 150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                games_completed += 1
                if games_completed >= MAX_GAMES:
                    game_state = EXIT_SCREEN
                else:
                    current_level = selected_level  # Stay on the same level
                    reset_game()
    elif game_state == EXIT_SCREEN:
        play_menu_music()
        return_menu = draw_exit_screen()
        if return_menu:
            game_state = MAIN_MENU
            score = [0, 0]
            games_completed = 0
            current_level = selected_level
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()