import pygame
from pygame import mixer
from LEVEL1 import Fighter  # Assuming Fighter is defined in LEVEL1.py
from PIL import Image

mixer.init()
pygame.init()

# Game window
SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 650
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

Samurai_Size = 128
Samurai_Scale = 2.55
Samurai_Offset = [55, 30]
Samurai_Data = [Samurai_Size, Samurai_Scale, Samurai_Offset]

Magician_Size = 128
Magician_Scale = 3
Magician_Offset = [55, 45]
Magician_Data = [Magician_Size, Magician_Scale, Magician_Offset]

# Sounds
# pygame.mixer.music.load("assets/audio/music.mp3")
# pygame.mixer.music.set_volume(0.5)
# pygame.mixer.music.play(-1, 0.0, 5000)
# sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
# sword_fx.set_volume(0.00)
# magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
# magic_fx.set_volume(0.00)

Samurai_fx = pygame.mixer.Sound("assets/audio/Samurai_sound/sword-blade-slicing-flesh-352708.mp3")
Samurai_fx.set_volume(0.1)

Samurai_attack_sound1 = pygame.mixer.Sound("assets/audio/Samurai_sound/sword-blade-slicing-flesh-352708.mp3")
Samurai_attack_sound1.set_volume(0.1)
# Samurai_attack_sound2 = pygame.mixer.Sound("assets/audio/Samurai_sound?")

bg_frames = []
bg_frame_index = 0
bg_animation_speed = 100  # milliseconds between frames
bg_last_update = pygame.time.get_ticks()

round_start_time = None
debuff_threshold = 10000  # 10 seconds in milliseconds
debuff_activated = False
debuff_warning_shown = False

def load_gif_frames(gif_path, brightness_factor=0.8):
    frames = []
    try:
        gif = Image.open(gif_path)
        frame_count = 0
        
        while True:
            try:
                # Convert PIL image to pygame surface
                frame = gif.copy()
                frame = frame.convert('RGBA')
                
                # Convert to pygame format
                pygame_image = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                ).convert_alpha()
                
                # Scale to screen size
                scaled_frame = pygame.transform.scale(pygame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                # Apply brightness adjustment
                if brightness_factor != 1.0:
                    scaled_frame = adjust_brightness(scaled_frame, brightness_factor)
                
                frames.append(scaled_frame)
                
                frame_count += 1
                gif.seek(frame_count)
                
            except EOFError:
                break
                
    except Exception as e:
        print(f"Error loading GIF: {e}")
        # Fallback to static image
        fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fallback.fill((50, 50, 100))  # Dark blue fallback
        frames.append(fallback)
    
    return frames

def adjust_brightness(surface, brightness_factor):
    if brightness_factor < 1.0:
        # Darken the image
        overlay = pygame.Surface(surface.get_size()).convert_alpha()
        brightness_value = int(255 * brightness_factor)
        overlay.fill((brightness_value, brightness_value, brightness_value, 255))
        
        # Create a copy and blend
        result = surface.copy()
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        return result
        
    elif brightness_factor > 1.0:
        # Brighten the image
        overlay = pygame.Surface(surface.get_size()).convert_alpha()
        brightness_value = int(255 * (brightness_factor - 1.0))
        overlay.fill((brightness_value, brightness_value, brightness_value, 255))
        
        # Create a copy and blend
        result = surface.copy()
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        return result
    
    else:
        # No change needed
        return surface

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
    global bg_frame_index, bg_last_update
    
    if current_level == 1:
        # Animated GIF background for level 1
        current_time = pygame.time.get_ticks()
        
        # Update frame if enough time has passed
        if current_time - bg_last_update > bg_animation_speed:
            bg_frame_index = (bg_frame_index + 1) % len(bg_frames_level1)
            bg_last_update = current_time
        
        # Draw current frame
        screen.blit(bg_frames_level1[bg_frame_index], (0, 0))
        
    elif current_level == 2:
        # Static background for level 2
        scaled_bg = pygame.transform.scale(bg_image2, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        
    elif current_level == 3:
        # Static background for level 3
        scaled_bg = pygame.transform.scale(bg_image3, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        
    else:
        # Fallback - use first frame of level 1 animation
        screen.blit(bg_frames_level1[0], (0, 0))

# Draw health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 504, 34))
    pygame.draw.rect(screen, RED, (x, y, 500, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 500 * ratio / 1.5, 30))

# Create fighters
def create_fighters():
    # f1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    # f2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    f1 = Fighter(1, 200, 310, False, Samurai_Data, Samurai_sheet, Samurai_Animation_Steps, Samurai_fx)
    f2 = Fighter(2, 1000, 310, True, Magician_Data, Magician_sheet, Magician_Animation_Steps, Samurai_fx)
    return f1, f2

def check_debuff_timer():
    global round_start_time, debuff_activated, debuff_warning_shown
    
    # Start timer when countdown finishes
    if intro_count <= 0 and round_start_time is None and not round_over and not game_over:
        round_start_time = pygame.time.get_ticks()
        print("Round timer started!")
    
    # Check if 10 seconds have passed
    if round_start_time is not None and not round_over and not game_over:
        elapsed_time = pygame.time.get_ticks() - round_start_time
        
        # Show warning at 8 seconds
        if elapsed_time >= 8000 and not debuff_warning_shown:
            debuff_warning_shown = True
            print("Warning: Debuff activating in 2 seconds!")
        
        # Activate debuff at 10 seconds
        if elapsed_time >= debuff_threshold and not debuff_activated:
            debuff_activated = True
            fighter_1.activate_debuff()
            fighter_2.activate_debuff()
            print("DEBUFF ACTIVATED! Both players losing 2 HP per second!")

def reset_timer():
    """Reset timer variables for new round"""
    global round_start_time, debuff_activated, debuff_warning_shown
    round_start_time = None
    debuff_activated = False
    debuff_warning_shown = False
    
def get_health_color(health, max_health):
    ratio = health / max_health
    if ratio > 0.6:
        return (0, 255, 0)    # Green
    elif ratio > 0.3:
        return (255, 255, 0)  # Yellow
    else:
        return (255, 0, 0)    # Red

# Background
bg_frames_level1 = load_gif_frames("assets/images/background/arenaOption4.gif")
bg_image2 = pygame.image.load("assets/images/background/background2.jpg").convert_alpha()
bg_image3 = pygame.image.load("assets/images/background/background3.jpg").convert_alpha()

# Spritesheets
Samurai_sheet = pygame.image.load("assets/images/Samurai/Sprites/Samurai_Spritelist.png").convert_alpha()
Magician_sheet = pygame.image.load("assets/images/Magician/Sprites/Wanderer_Magican_Spritelist.png").convert_alpha()

# Victory image
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

# animation steps
Samurai_Animation_Steps = [6, 8, 8, 12, 6, 4, 3, 2, 2, 3]
Magician_Animation_Steps = [8, 7, 8, 7, 9, 16, 11, 8, 2, 4]

# Fonts 
count_font = pygame.font.Font("assets/fonts/VTFRedzone-Classic.ttf", 120)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
stage_font = pygame.font.Font("assets/fonts/turok.ttf", 60)
timer_font = pygame.font.Font("assets/fonts/turok.ttf", 20)
debuff_font = pygame.font.Font("assets/fonts/turok.ttf", 24)

# create fighters
fighter_1, fighter_2 = create_fighters()

# Game loop
run = True
game_over = False
winner = None  # Track the winner after Level 3
    

while run:
    clock.tick(FPS)

    draw_bg()

    health_font = pygame.font.Font("assets/fonts/turok.ttf", 20)
    p1_health_color = get_health_color(fighter_1.health, 150)
    p2_health_color = get_health_color(fighter_2.health, 150)

    # Show health and scores
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 820, 20)
    draw_text("Round 1", stage_font, WHITE, 585, 8)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 55)
    draw_text("P2: " + str(score[1]), score_font, RED, 820, 55)
    draw_text(f"HP: {fighter_1.health}/150", health_font, p1_health_color, 430, 52)
    draw_text(f"HP: {fighter_2.health}/150", health_font, p2_health_color, 1230, 52)

    # Check debuff timer
    check_debuff_timer()
    
    # Show timer and debuff status
    if round_start_time is not None and not round_over and not game_over:
        elapsed_time = (pygame.time.get_ticks() - round_start_time) // 1000
        time_remaining = max(0, 10 - elapsed_time)
        
        if debuff_activated:
            draw_text("DEBUFF ACTIVE!", debuff_font, RED, SCREEN_WIDTH // 2 - 70, 100)
        elif debuff_warning_shown:
            draw_text(f"DEBUFF IN: {time_remaining}", debuff_font, YELLOW, SCREEN_WIDTH // 2 - 70, 100)
        
        draw_text(f"Time: {elapsed_time}s", timer_font, WHITE, SCREEN_WIDTH // 2 - 35, 70)
    # Countdown logic
    if intro_count <= 0 and not game_over:
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        # draw_text("FIGHT", count_font, RED, SCREEN_WIDTH / 2 - 30, SCREEN_HEIGHT / 3 - 20)
    elif not game_over:
        draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2 - 30, SCREEN_HEIGHT / 3 + 20)
        
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # FIXED: Update fighters with proper screen width for projectiles
    fighter_1.update(SCREEN_WIDTH)  # Pass screen width for projectile updates
    fighter_2.update(SCREEN_WIDTH)  # Pass screen width for projectile updates
    
    # Check projectile collisions
    fighter_1.check_projectile_collision(fighter_2)
    fighter_2.check_projectile_collision(fighter_1)
    
    # Draw fighters (this will also draw their projectiles)
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    # Debug: Draw projectile info
    if len(fighter_1.projectiles) > 0 or len(fighter_2.projectiles) > 0:
        debug_y = 130
        for i, proj in enumerate(fighter_1.projectiles):
            if proj.active:
                draw_text(f"P1 Bolt {i}: x={int(proj.x)}, dir={proj.direction}", 
                         pygame.font.Font(None, 20), WHITE, 10, debug_y + i * 20)
        
        for i, proj in enumerate(fighter_2.projectiles):
            if proj.active:
                draw_text(f"P2 Bolt {i}: x={int(proj.x)}, dir={proj.direction}", 
                         pygame.font.Font(None, 20), WHITE, 800, debug_y + i * 20)


    # Check for round over
    if not round_over and not game_over:
        if not fighter_1.alive:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            reset_timer()  # Reset timer when round ends
            if current_level == MAX_LEVEL:
                winner = 2
                game_over = True
                game_over_time = pygame.time.get_ticks()
        elif not fighter_2.alive:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            reset_timer()  # Reset timer when round ends
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
            bg_frame_index = 0
            reset_timer()  # Reset timer for new game
            fighter_1, fighter_2 = create_fighters()

        elif exit_game:
            run = False

    # If round over but game not finished
    elif round_over:
        screen.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            reset_timer()  # Reset timer for next round

            # LEVEL TRANSITION
            current_level += 1
            if current_level > MAX_LEVEL:
                current_level = MAX_LEVEL
                game_over = True
                game_over_time = pygame.time.get_ticks()
            else:
                bg_frame_index = 0
                fighter_1, fighter_2 = create_fighters()

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
