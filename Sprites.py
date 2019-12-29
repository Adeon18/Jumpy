# Sprite classes for platform game
import pygame
import random
from settings import *
from random import choice

vec = pygame.math.Vector2

class Spritesheet1:
    # Utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet1 = pygame.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab an image out of a spritesheet
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet1, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width // 2, height // 2))
        return image

class Resize:
    def __init__(self, image):
        pass

    def get_image(self, image, width, height):
        # Grab an image out of a spritesheet
        image = pygame.transform.scale(image, (width // 2, height // 2))
        return image

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.invincible = False
        self.current_frame = 0
        self.last_invincible = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)
        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.friction = PLAYER_FRICTION

    def load_images(self):

        # Standing frames for 2 cases:default and invincible
        self.standing_frames = [self.game.spritesheet1.get_image(614, 1063, 120, 191),
                         self.game.spritesheet1.get_image(690, 406, 120, 201)]
        self.standing_frames_inv = [Resize.get_image(self, pygame.image.load('graphics/bunny1_inv_stand.png'), 211, 215),
                                Resize.get_image(self, pygame.image.load('graphics/bunny1_inv_ready.png'), 211, 215)]
        # Clearing the black square around the frames
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        for frame in self.standing_frames_inv:
            pygame.transform.scale(frame, (211 // 2, 215 // 2))
        # Walking frames for 2 cases
        self.walking_frames_R = [self.game.spritesheet1.get_image(678, 860, 120, 201),
                                 self.game.spritesheet1.get_image(692, 1458, 120, 207)]
        self.walking_frames_inv_R = [Resize.get_image(self, pygame.image.load('graphics/bunny1_inv_walk1.png'), 211, 215),
                                 Resize.get_image(self, pygame.image.load('graphics/bunny1_inv_walk2.png'), 211, 215)]
        self.walking_frames_L = []
        self.walking_frames_inv_L = []
        # Applying the L frames in both cases
        for frame in self.walking_frames_R:
            frame.set_colorkey(BLACK)
            # 1 - horisontal , 2 - vertical
            self.walking_frames_L.append(pygame.transform.flip(frame, True, False))
        for frame in self.walking_frames_inv_R:
            pygame.transform.scale(frame, (211 // 2, 215 // 2))
            # 1 - horisontal , 2 - vertical
            self.walking_frames_inv_L.append(pygame.transform.flip(frame, True, False))
        # Setting the jumping frame for both cases and removing the black squares
        self.jumping_frame = self.game.spritesheet1.get_image(382, 763, 150, 181)
        self.jumping_frame.set_colorkey(BLACK)
        self.jumping_frame_inv = Resize.get_image(self, pygame.image.load('graphics/bunny1_inv_jump.png'), 211, 215)
        pygame.transform.scale(self.jumping_frame_inv, (211 // 2, 215 // 2))

    def jump(self):
        # jump only if standing on a platform
        self.rect.x += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP_V
            self.game.jump_sound.play()

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -10:
                self.vel.y = -10

    def update(self):
        self.animation()
        self.acc = vec(0, PLAYER_GRAV)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_d]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * self.friction

        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.5: # If the vel < 0.5 we stop
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        # wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos


    def animation(self):
        time_passed = pygame.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Show walking animation
        if self.walking:
            if time_passed - self.last_update > 140:
                self.last_update = time_passed
                if self.invincible:
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_inv_L)
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_L)
                rect_bottom = self.rect.bottom
                if self.vel.x > 0:
                    if self.invincible:
                        self.image = self.walking_frames_inv_R[self.current_frame]
                    else:
                        self.image = self.walking_frames_R[self.current_frame]
                else:
                    if self.invincible:
                        self.image = self.walking_frames_inv_L[self.current_frame]
                    else:
                        self.image = self.walking_frames_L[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = rect_bottom
        # Show jumping animation
        if self.jumping and not self.walking:
            rect_bottom = self.rect.bottom
            if self.invincible:
                self.image = self.jumping_frame_inv
            else:
                self.image = self.jumping_frame
            self.rect = self.image.get_rect()
            self.rect.bottom = rect_bottom

        # Show standing animation
        if not self.jumping and not self.walking:
            if time_passed - self.last_update > 350:
                self.last_update = time_passed
                if self.invincible:
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_inv)
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                rect_bottom = self.rect.bottom
                if self.invincible:
                    self.image = self.standing_frames_inv[self.current_frame]
                else:
                    self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = rect_bottom

        self.mask = pygame.mask.from_surface(self.image)



class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Platform images
        snowy_images = [self.game.spritesheet1.get_image(0, 768, 380, 94),
                        self.game.spritesheet1.get_image(213, 1764, 201, 100)]
        normal_images = [self.game.spritesheet1.get_image(0, 288, 380, 94),
                         self.game.spritesheet1.get_image(213, 1662, 201, 100)]
        stone_images = [self.game.spritesheet1.get_image(0, 96, 380, 94),
                        self.game.spritesheet1.get_image(382, 408, 200, 100)]
        wood_images = [self.game.spritesheet1.get_image(0, 960, 380, 94),
                       self.game.spritesheet1.get_image(218, 1558, 200, 100)]
        pink_images = [self.game.spritesheet1.get_image(0, 576, 380, 94),
                       self.game.spritesheet1.get_image(218, 1456, 201, 100)]
        # Platform choices
        if 250 > self.game.score >= 0:
            if random.randrange(100) < 90:
                self.type = 'normal'
            else:
                self.type = 'snowy'
            #self.type = choice(['normal', 'snowy'])
        if 500 > self.game.score >= 250:
            if random.randrange(100) < 75:
                self.type = 'normal'
            else:
                self.type = 'snowy'
            #self.type = choice(['wooden', 'snowy'])
        if 750 > self.game.score >= 500:
            if random.randrange(100) < 60:
                self.type = 'stone'
            else:
                self.type = 'snowy'
            #self.type = choice(['stone', 'snowy'])
        if 1000 > self.game.score >= 750:
            if random.randrange(100) < 50:
                self.type = 'pink'
            else:
                self.type = 'snowy'
            #self.type = choice(['pink', 'snowy'])
        if 10000 > self.game.score >= 1000:
            self.type = choice(['snowy'])

        # Platform images attachment
        if self.type == 'normal':
            self.image = random.choice(normal_images)
        elif self.type == 'wooden':
            self.image = random.choice(wood_images)
        elif self.type == 'stone':
            self.image = random.choice(stone_images)
        elif self.type == 'pink':
            self.image = random.choice(pink_images)
        elif self.type == 'snowy':
            self.image = random.choice(snowy_images)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Applying the sprites spawning on platform
        if random.randrange(100) < POWERUP_SPAWN_RATIO and not game.player.invincible:
            Powerup(self.game, self)
        if random.randrange(100) < COIN_SPAWN_RATIO:
            Coin(self.game, self)
        if random.randrange(100) < SPIKEY_SPAWN_RATIO and self.image == normal_images[0]:
            Spikey(self.game, self)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = choice(['boost', 'bubble'])
        if self.type == 'boost':
            self.image = self.game.spritesheet1.get_image(820, 1805, 71, 70)
        elif self.type == 'bubble':
            self.image = self.game.spritesheet1.get_image(826, 134, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 2
        self.jumpCount = 1.2

    def update(self):
        # Checking if the powerup is out of the screen or on it
        if self.rect.y >= 0:
            if self.jumpCount >= -2:

                self.jumpCount -= 0.1
                self.rect.y -= (self.jumpCount * abs(self.jumpCount)) * 0.5
            else:
                self.jumpCount = 1.2
                self.rect.bottom = self.plat.rect.top - 2
        # Else if the powerup is above the screen we change the signs
        else:
            if self.jumpCount >= 2:

                self.jumpCount -= 0.1
                self.rect.y -= (self.jumpCount * abs(self.jumpCount)) * 0.5
            else:
                self.jumpCount = 1.2
                self.rect.bottom = self.plat.rect.top - 2

        if not self.game.platforms.has(self.plat):
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.coins
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.last_update = 0
        self.current_frame = 0
        self.load_images()
        self.image = self.animation[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5

    def load_images(self):
        self.animation = [self.game.spritesheet1.get_image(698, 1931, 84, 84),
                       self.game.spritesheet1.get_image(829, 0, 66, 84),
                       self.game.spritesheet1.get_image(897, 1574, 50, 84),
                       self.game.spritesheet1.get_image(645, 651, 15, 84),
                       pygame.transform.flip(self.game.spritesheet1.get_image(897, 1574, 50, 84), True, False),
                       pygame.transform.flip(self.game.spritesheet1.get_image(829, 0, 66, 84), True, False)]

        for image in self.animation:
            image.set_colorkey(BLACK)



    def update(self):
        time_passed = pygame.time.get_ticks()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        self.mask = pygame.mask.from_surface(self.image)
        if time_passed - self.last_update > 100:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            if Coin:
                self.image = self.animation[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.centerx = self.plat.rect.centerx
            self.rect.bottom = self.plat.rect.top - 5
        if not self.game.platforms.has(self.plat):
            self.kill()


class Mob(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_up = self.game.spritesheet1.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet1.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice([-100,WIDTH + 100])
        self.velx = random.randrange(1, 4)
        self.vely = 0
        self.dy = 0.5
        if self.rect.centerx > WIDTH:
            self.velx *= -1
        self.rect.y = random.randrange(HEIGHT / 3)

    def update(self):
        self.rect.x += self.velx
        self.vely += self.dy
        if self.vely > 3 or self.vely < -3:
            self.dy *= -1
        rect_center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = rect_center
        self.rect.y += self.vely
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.velx *= -1
        if self.rect.centery > HEIGHT + 100:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = CLOUD_LAYER
        self.groups = game.all_sprites, game.clouds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = random.choice(self.game.cloud_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        scale = random.randrange(50, 100) / 100
        self.image = pygame.transform.scale(self.image, (int(self.rect.width * scale), int(self.rect.height * scale)))
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-500, 50)

    def update(self):
        if self.rect.top > HEIGHT * 2:
            self.kill()

class Spikey(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.load_images()
        self.current_frame = 0
        self.last_update = 0
        self.image = self.images_R[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 1
        self.velx = random.randrange(1, 2)
        self.vely = 0
        self.walking = False


    def load_images(self):
        self.images_R = [self.game.spritesheet1.get_image(704, 1256, 120, 159),
                         self.game.spritesheet1.get_image(812, 296, 90, 155)]
        for image in self.images_R:
            image.set_colorkey(BLACK)

        self.images_L = [pygame.transform.flip(self.game.spritesheet1.get_image(704, 1256, 120, 159), True, False),
                         pygame.transform.flip(self.game.spritesheet1.get_image(812, 296, 90, 155), True, False)]
        for image in self.images_L:
            image.set_colorkey(BLACK)
        self.stand_image = self.game.spritesheet1.get_image(814, 1417, 90, 155)
        self.stand_image.set_colorkey(BLACK)

    def update(self):
        time_passed = pygame.time.get_ticks()
        self.rect.x += self.velx

        if self.rect.right > self.plat.rect.right - 4:
            self.velx -= 0.07
        elif self.rect.left < self.plat.rect.left + 7:
            self.velx += 0.07

        if time_passed - self.last_update > 185:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.images_R)
            rect_bottom = self.rect.bottom
            centerx = self.rect.centerx
            if self.velx > 0:
                self.image = self.images_R[self.current_frame]
                self.rect.x += self.velx
            elif self.velx < 0:
                self.image = self.images_L[self.current_frame]
                self.rect.x += self.velx
            self.rect = self.image.get_rect()
            self.rect.centerx = centerx
            self.rect.bottom = rect_bottom




