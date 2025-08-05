import numpy as np
import pygame

RED = (255,0,0)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = np.random.uniform(-5, 5)
        self.vel_y = np.random.uniform(-8, -2)
        self.gravity = 0.3
        self.life = 60  # frames
        self.max_life = 60
        self.size = np.random.randint(2, 5)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            temp_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color = (*RED[:3], alpha)
            pygame.draw.circle(temp_surf, color, (self.size, self.size), self.size)
            screen.blit(temp_surf, (int(self.x - self.size), int(self.y - self.size)))


class Ball:
    def __init__(self, x, y, target_x, target_y, velocity, screen_height, screen_width, particles):
        self.x = x
        self.y = y
        self.radius = 15
        self.velocity = velocity
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.particles = particles

        dx = target_x - x
        dy = target_y - y
        distance = (dx**2 + dy**2)**0.5

        if distance > 0:
            self.vel_x = (dx / distance) * velocity
            self.vel_y = (dy / distance) * velocity
        else:
            self.vel_x = 0
            self.vel_y = 0

        self.sprite_sheet = pygame.image.load("assets/images/ball/splash.png").convert_alpha()
        self.splash_images = self.load_images()

        self.is_splashing = False
        self.splash_frame = 0
        self.splash_animation_speed = 0.3
        self.splash_x = 0
        self.splash_y = 0

        self.active = True

    def update(self):
        if self.is_splashing:
            # update splash animation
            self.splash_frame += self.splash_animation_speed
            if self.splash_frame >= len(self.splash_images):
                # animation finished
                self.is_splashing = False
                self.active = False
            return

        if self.active:
            self.x += self.vel_x
            self.y += self.vel_y

            ground_level = self.screen_height - 50
            if self.y >= ground_level:
                self.disintegrate()
                return

            # remove ball if it goes off screen
            if (self.x < -50 or self.x > self.screen_width + 50 or
                self.y < -50 or self.y > self.screen_height + 50):
                self.active = False

    def disintegrate(self):
        self.is_splashing = True
        self.splash_x = self.x
        self.splash_y = self.screen_height - 50
        self.splash_frame = 0

        # create particles at ball position
        for _ in range(15):  # number of particles
            self.particles.append(Particle(self.x, self.y))

    def draw(self, screen):
        if self.is_splashing:
            # draw splash animation
            if int(self.splash_frame) < len(self.splash_images):
                splash_img = self.splash_images[int(self.splash_frame)]
                # center the splash image at the splash position
                splash_rect = splash_img.get_rect(center=(int(self.splash_x), int(self.splash_y)))
                screen.blit(splash_img, splash_rect)
        elif self.active:
            # draw ball trail
            for i in np.linspace(0, 15, 20):
                alpha = max(0, (15 - i) * 15)

                trail_x = self.x - self.vel_x * i * 0.12
                trail_y = self.y - self.vel_y * i * 0.12

                temp_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*RED[:3], int(alpha)), (self.radius, self.radius), self.radius)

                screen.blit(temp_surf, (int(trail_x - self.radius), int(trail_y - self.radius)))

    def check_collision(self, fighter):
        if not self.active or self.is_splashing:
            return False

        fighter_center_x = fighter.rect.centerx
        fighter_center_y = fighter.rect.centery

        distance = ((self.x - fighter_center_x)**2 + (self.y - fighter_center_y)**2)**0.5

        if distance < self.radius + 30:  # 30 is approximate fighter collision radius
            self.active = False
            return True
        return False

    def load_images(self):
        animation_list = []
        for x in range(7):
            temp_img = self.sprite_sheet.subsurface(x * 64, 0, 64, 64)
            animation_list.append(pygame.transform.scale(temp_img, (64 * 2, 64 * 2)))
        return animation_list

