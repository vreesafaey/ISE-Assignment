import pygame


class Projectile:
    def __init__(self, x, y, direction, speed=15, damage=15):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.speed = speed
        self.damage = damage
        self.active = True
        self.width = 30
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self, screen_width):
        # Move the projectile
        self.x += self.speed * self.direction
        self.rect.x = self.x
        
        # Remove projectile if it goes off screen
        if self.x < 0 or self.x > screen_width:
            self.active = False
    
    def draw(self, surface):
        # Draw a simple electric bolt (you can replace this with a sprite)
        pygame.draw.ellipse(surface, (255, 255, 0), self.rect)  # Yellow bolt
        pygame.draw.ellipse(surface, (255, 255, 255), (self.rect.x + 5, self.rect.y + 3, 20, 9))  # White center


class Fighter():

  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
    current_level = 1
    self.player = player
    self.size = data[0]
    self.image_scale = data[1]
    self.offset = data[2]
    self.flip = flip
    self.animation_list = self.load_images(sprite_sheet, animation_steps)
    self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
    self.frame_index = 0
    self.image = self.animation_list[self.action][self.frame_index]
    self.update_time = pygame.time.get_ticks()
    self.rect = pygame.Rect((x, y, 80, 180))
    self.vel_y = 0
    self.running = False
    self.jump = False
    self.attacking = False
    self.attack_type = 0
    self.attack_cooldown = 0
    self.attack_sound = sound
    self.hit = False
    self.health = 150
    self.alive = True
    self.debuff_active = False
    self.debuff_frame_counter = 0
    self.debuff_damage_interval_frames = 60
    
    # Projectile system
    self.projectiles = []
    self.bolt_fired = False  # Track if bolt has been fired in current attack
    self.magic_attack_frame = 6  # Frame when bolt should be fired (after 6 movement frames)

  def load_images(self, sprite_sheet, animation_steps):
    #extract images from spritesheet
    animation_list = []
    for y, animation in enumerate(animation_steps):
      temp_img_list = []
      for x in range(animation):
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)
    return animation_list

  def move(self, screen_width, screen_height, surface, target, round_over):
    SPEED = 10
    GRAVITY = 2
    dx = 0
    dy = 0
    self.running = False
    self.attack_type = 0

    #get keypresses
    key = pygame.key.get_pressed()

    #can only perform other actions if not currently attacking
    if self.attacking == False and self.alive == True and round_over == False:
      #check player 1 controls
      if self.player == 1:
        #movement
        if key[pygame.K_a]:
          dx = -SPEED
          self.running = True
        if key[pygame.K_d]:
          dx = SPEED
          self.running = True
        #jump
        if key[pygame.K_w] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #attack
        if key[pygame.K_r] or key[pygame.K_t]:
          self.attack(target)
          #determine which attack type was used
          if key[pygame.K_r]:
            self.attack_type = 1
          if key[pygame.K_t]:
            self.attack_type = 2

      #check player 2 controls
      if self.player == 2:
        #movement
        if key[pygame.K_LEFT]:
          dx = -SPEED
          self.running = True
        if key[pygame.K_RIGHT]:
          dx = SPEED
          self.running = True
        #jump
        if key[pygame.K_UP] and self.jump == False:
          self.vel_y = -30
          self.jump = True
        #attack
        if key[pygame.K_l] or key[pygame.K_m]:
          self.attack(target)
          #determine which attack type was used
          if key[pygame.K_l]:
            self.attack_type = 1
          if key[pygame.K_m]:
            self.attack_type = 2

    #apply gravity
    self.vel_y += GRAVITY
    dy += self.vel_y

    #ensure player stays on screen
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right
    if self.rect.bottom + dy > screen_height - 110:
      self.vel_y = 0
      self.jump = False
      dy = screen_height - 110 - self.rect.bottom

    #ensure players face each other
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True

    #apply attack cooldown
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1

    #update player position
    self.rect.x += dx
    self.rect.y += dy

  # METHOD 1: Single update function with player-specific logic
  def update(self, screen_width=1350):
        if self.player == 1:
            self.update_fighter1()
        else:
            self.update_fighter2()
        
        # Update all projectiles with correct screen width
        self.update_projectiles(screen_width)

  def update_projectiles(self, screen_width):
      """Update all active projectiles"""
      for projectile in self.projectiles[:]:  # Use slice to avoid modification during iteration
          if projectile.active:
              projectile.update(screen_width)
          else:
              self.projectiles.remove(projectile)

  def check_projectile_collision(self, target):
      """Check if any projectile hits the target"""
      for projectile in self.projectiles[:]:
          if projectile.active and projectile.rect.colliderect(target.rect):
              # Hit the target
              target.health -= projectile.damage
              target.hit = True
              # Remove the projectile
              projectile.active = False
              self.projectiles.remove(projectile)
              print(f"Projectile hit! Target health: {target.health}")

  def fire_magic_bolt(self):
      """Fire a magic bolt projectile"""
      if not self.bolt_fired:
          # Calculate bolt starting position
          bolt_x = self.rect.centerx + (50 if not self.flip else - 50)
          bolt_y = self.rect.centery - 20
          
          # Create projectile moving in the direction the fighter is facing
          direction = -1 if self.flip else 1
          bolt = Projectile(bolt_x, bolt_y, direction, speed=20, damage=15)
          self.projectiles.append(bolt)
          self.bolt_fired = True
          print(f"Magic bolt fired by player {self.player}!")

  def update_fighter1(self):
    self.apply_debuff_damage()
    """Animation update logic specific to Fighter 1"""
    #check what action the player is performing
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(9)#6:death
    elif self.hit == True:
      self.update_action(8)#5:hit
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(4)#3:attack1
      elif self.attack_type == 2:
        self.update_action(6)#4:attack2
    elif self.jump == True:
      self.update_action(3)#2:jump
    elif self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    # Fighter 1 specific animation speed
    animation_cooldown = 50
    self._handle_animation_frame(animation_cooldown)

  def update_fighter2(self):
    self.apply_debuff_damage()
    """Animation update logic specific to Fighter 2"""
    #check what action the player is performing
    if self.health <= 0:
      self.health = 0
      self.alive = False
      self.update_action(9)#6:death
    elif self.hit == True:
      self.update_action(8)#5:hit
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:attack1
      elif self.attack_type == 2:
        self.update_action(4)#4:attack2
    elif self.jump == True:
      self.update_action(7)#2:jump
    elif self.running == True:
      self.update_action(1)#1:run
    else:
      self.update_action(0)#0:idle

    # Fighter 2 specific animation speed (different from Fighter 1)
    animation_cooldown = 60  # Slower animation for fighter 2
    self._handle_animation_frame(animation_cooldown)

  def apply_debuff_damage(self):
    """Apply debuff damage if debuff is active"""
    if self.debuff_active and self.alive:
        self.debuff_frame_counter += 1
        
        # Apply damage every 60 frames (1 second at 60 FPS)
        if self.debuff_frame_counter >= self.debuff_damage_interval_frames:
            old_health = self.health
            self.health -= 2
            self.debuff_frame_counter = 0  # Reset counter
            
            print(f"Player {self.player} debuff damage: {old_health} -> {self.health}")
            
            if self.health <= 0:
                self.health = 0
                self.alive = False

  def activate_debuff(self):
      """Activate the debuff system"""
      if not self.debuff_active:
          self.debuff_active = True
          self.last_debuff_damage = pygame.time.get_ticks()
          print(f"Player {self.player} debuff activated!")

  def deactivate_debuff(self):
      """Deactivate the debuff system"""
      self.debuff_active = False
      print(f"Player {self.player} debuff deactivated!")
            
  def _handle_animation_frame(self, animation_cooldown):
    """Common animation frame handling logic"""
    #update image
    self.image = self.animation_list[self.action][self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list[self.action]):
      #if the player is dead then end the animation
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #check if an attack was executed
        if self.action == 3 or self.action == 4 or self.action == 5 or self.action == 6:
          self.attacking = False
          self.attack_cooldown = 5
        #check if damage was taken
        if self.action == 8:
          self.hit = False
          #if the player was in the middle of an attack, then the attack is stopped
          self.attacking = False
          self.attack_cooldown = 20

  def attack(self, target):
    if self.attack_cooldown == 0:
      #execute attack
      self.attacking = True
      
      if self.attack_type == 1:
        self.attack_sound.play()
      else:
        self.attack_sound.play()
        
      attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
      if attacking_rect.colliderect(target.rect):
        target.health -= 10
        target.hit = True

  def update_action(self, new_action):
    #check if the new action is different to the previous one
    if new_action != self.action:
      self.action = new_action
      #update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
        
        # Draw all projectiles
        for projectile in self.projectiles:
            if projectile.active:
                projectile.draw(surface)