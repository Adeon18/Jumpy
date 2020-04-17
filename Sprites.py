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
        # We divide width and height by 2 cuz the spritesheet is too big for us
        image = pygame.transform.scale(image, (width // 2, height // 2))
        return image


def Get_image_res(image, resize_ratio):
    width, height = image.get_size()
    image = pygame.transform.scale(image, (width // resize_ratio, height // resize_ratio))
    return image


class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.menu
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet1.get_image(0, 96, 380, 94)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.game.screen.blit(self.image, self.rect)

    def draw_txt(self, text, size, color):
        font = pygame.font.Font('fonts/AmaticSC-Bold.ttf', size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        self.game.screen.blit(text_surface, text_rect)

    def update(self):
        pygame.transform.scale(self.image, (380 * 2, 94 * 2))


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Move properties
        self.walking = False
        self.jumping = False
        # Pow properties
        self.has_bubble = False
        self.has_jetpack = False
        self.has_wings = False
        # Jet properties
        self.acceleration = False
        self.still = False
        self.losing_wings = False
        # Anmation properties
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[1]
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
        self.standing_frames_inv = [Get_image_res(pygame.image.load('graphics/bunny1_inv_stand.png'), 2),
                                    Get_image_res(pygame.image.load('graphics/bunny1_inv_ready.png'), 2)]
        # Clearing the black square around the frames
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        for frame in self.standing_frames_inv:
            pygame.transform.scale(frame, (211 // 2, 215 // 2))
        # Walking frames for 2 cases
        self.walking_frames_R = [self.game.spritesheet1.get_image(678, 860, 120, 201),
                                 self.game.spritesheet1.get_image(692, 1458, 120, 207)]
        self.walking_frames_inv_R = [Get_image_res(pygame.image.load('graphics/bunny1_inv_walk1.png'), 2),
                                     Get_image_res(pygame.image.load('graphics/bunny1_inv_walk2.png'), 2)]
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
        # Player/jetpack images
        self.jet_start_frames = [Get_image_res(pygame.image.load('graphics/player_jet_start1.png'), 2),
                                 Get_image_res(pygame.image.load('graphics/player_jet_start2.png'), 2)]
        for image in self.jet_start_frames:
            image.set_colorkey(BLACK)
        self.jet_go_frames = [Get_image_res(pygame.image.load('graphics/player_jet1.png'), 2),
                              Get_image_res(pygame.image.load('graphics/player_jet2.png'), 2)]
        for image in self.jet_go_frames:
            image.set_colorkey(BLACK)
        # Player with wings images
        self.has_wings_frames = [Get_image_res(pygame.image.load('graphics/player_fly1.png'), 2),
                                 Get_image_res(pygame.image.load('graphics/player_fly2.png'), 2),
                                 Get_image_res(pygame.image.load('graphics/player_fly3.png'), 2),
                                 Get_image_res(pygame.image.load('graphics/player_fly4.png'), 2),
                                 Get_image_res(pygame.image.load('graphics/player_fly5.png'), 2)]
        # Jump frames
        self.jumping_frame = self.game.spritesheet1.get_image(382, 763, 150, 181)
        self.jumping_frame.set_colorkey(BLACK)
        self.jumping_frame_inv = Get_image_res(pygame.image.load('graphics/bunny1_inv_jump.png'), 2)

    def jump(self):
        # Jump only if standing on a platform and without a pow
        self.rect.x += 2
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping and not self.has_jetpack and not self.has_wings and not self.has_bubble:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP_V
            #self.game.jump_sound.play()

    def jump_cut(self):
        # The code that cuts the jump
        if self.jumping and not self.has_jetpack and not self.has_wings and not self.has_bubble:
            if self.vel.y < -10:
                self.vel.y = -10

    def update(self):
        self.animation()
        # Applying gravity
        if self.has_bubble or self.has_jetpack or self.has_wings:
            self.acc = vec(0, 0)
        else:
            self.acc = vec(0, PLAYER_GRAV)
        # Applying movement
        keys = pygame.key.get_pressed()
        # With wings
        if self.has_wings:
            if keys[pygame.K_a]:
                self.acc.x = -PLAYER_FLY_ACC
            if keys[pygame.K_d]:
                self.acc.x = PLAYER_FLY_ACC
        # Without wings
        else:
            if keys[pygame.K_a]:
                self.acc.x = -PLAYER_ACC
            if keys[pygame.K_d]:
                self.acc.x = PLAYER_ACC

        # Apply friction
        self.acc.x += self.vel.x * self.friction

        # Equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.5:  # If the vel < 0.5 we stop
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        # Wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        # If player has wings we move him down the screen
        if self.has_wings:
            self.pos.y += 3
            if self.pos.y >= SCR_CHANGE_H_FLY + 10:
                self.pos.y = SCR_CHANGE_H_FLY + 10
        # If player is about to lose wings we move him up the screen so he does not fall immediately after wing loss
        if self.losing_wings:
            self.pos.y -= 4
            if self.pos.y <= SCR_CHANGE_H:
                self.pos.y = SCR_CHANGE_H

        self.rect.midbottom = self.pos

    def animation(self):
        time_passed = pygame.time.get_ticks()
        # We define when the player is considered to be moving
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        # Show walking animation
        if self.walking and not self.has_jetpack and not self.has_wings:
            if time_passed - self.last_update > 140:
                self.last_update = time_passed
                if self.has_bubble:
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_inv_L)
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.walking_frames_L)
                rect_bottom = self.rect.bottom
                if self.vel.x > 0:
                    if self.has_bubble:
                        self.image = self.walking_frames_inv_R[self.current_frame]
                    else:
                        self.image = self.walking_frames_R[self.current_frame]
                else:
                    if self.has_bubble:
                        self.image = self.walking_frames_inv_L[self.current_frame]
                    else:
                        self.image = self.walking_frames_L[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = rect_bottom

        # Show jumping animation
        if self.jumping and not self.walking and not self.has_jetpack and not self.has_wings:
            rect_bottom = self.rect.bottom
            if self.has_bubble:
                self.image = self.jumping_frame_inv
            else:
                self.image = self.jumping_frame
            self.rect = self.image.get_rect()
            self.rect.bottom = rect_bottom

        # Show standing animation
        if not self.jumping and not self.walking and not self.has_jetpack and not self.has_wings:
            if time_passed - self.last_update > 350:
                self.last_update = time_passed
                if self.has_bubble:
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_inv)
                else:
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                rect_bottom = self.rect.bottom
                if self.has_bubble:
                    self.image = self.standing_frames_inv[self.current_frame]
                else:
                    self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = rect_bottom

        # Show jetpack animation
        if self.has_jetpack and not self.has_wings:
            if time_passed - self.last_update > 50:
                self.last_update = time_passed
                if self.acceleration:
                    self.current_frame = (self.current_frame + 1) % len(self.jet_start_frames)
                    self.image = self.jet_start_frames[self.current_frame]
                if self.still:
                    self.current_frame = (self.current_frame + 1) % len(self.jet_go_frames)
                    self.image = self.jet_go_frames[self.current_frame]
        # Show wing animation
        if self.has_wings:
            if time_passed - self.last_update > 90:
                self.last_update = time_passed
                self.current_frame = (self.current_frame + 1) % len(self.has_wings_frames)
                rect_center = self.rect.centerx
                self.image = self.has_wings_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.centerx = rect_center

        self.mask = pygame.mask.from_surface(self.image)


class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLATFORM_LAYER
        self.groups = game.all_sprites, game.platforms
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = None
        # Move properties
        self.on_move = False
        self.on_move_x = False
        self.on_move_y = False
        # Mob properties
        self.has_spikey = False
        self.has_cloud = False
        self.has_pow = False
        self.has_coin = False
        self.has_wingman = False
        self.has_mob = False
        # Respawn property
        self.respawn = False
        # Plat speed properties
        self.vel_x = 1
        self.vel_y = 1
        self.count_vel_y = 0
        if self.has_spikey or self.has_cloud or self.has_wingman:
            self.has_mob = True
        # Applying the chances of spawning a moving plat
        if random.randrange(100) < MOVING_PLAT_SPAWN_RATIO and self.game.score > 200:
            self.on_move = True
        # Defining the move type
        if self.on_move:
            if random.randrange(100) < 90:
                self.on_move_x = True
            else:
                self.on_move_y = True
        # Platform images
        snowy_images = [self.game.spritesheet1.get_image(0, 768, 380, 94),
                        self.game.spritesheet1.get_image(213, 1764, 201, 100)]
        icy_images = [Get_image_res(pygame.image.load('graphics/ice_plat_l.png'), 2),
                      Get_image_res(pygame.image.load('graphics/ice_plat_s.png'), 2)]
        normal_images = [self.game.spritesheet1.get_image(0, 288, 380, 94),
                         self.game.spritesheet1.get_image(213, 1662, 201, 100)]
        stone_images = [self.game.spritesheet1.get_image(0, 96, 380, 94),
                        self.game.spritesheet1.get_image(382, 408, 200, 100)]
        wood_images = [self.game.spritesheet1.get_image(0, 960, 380, 94),
                       self.game.spritesheet1.get_image(218, 1558, 200, 100)]
        pink_images = [self.game.spritesheet1.get_image(0, 576, 380, 94),
                       self.game.spritesheet1.get_image(218, 1456, 201, 100)]
        sand_images = [self.game.spritesheet1.get_image(0, 672, 380, 94),
                       self.game.spritesheet1.get_image(208, 1879, 201, 100)]
        # Platform choices
        if PLAT_STONE_START > self.game.score >= PLAT_NM_START:
            if random.randrange(100) < 90:
                self.type = 'normal'
            else:
                self.type = 'sand'
            # self.type = choice(['wooden', 'snowy'])
        if PLAT_PINK_START > self.game.score >= PLAT_STONE_START:
            if random.randrange(100) < 90:
                self.type = 'stone'
            else:
                self.type = 'sand'
            # self.type = choice(['stone', 'snowy'])
        if PLAT_SNOW_START > self.game.score >= PLAT_PINK_START:
            if random.randrange(100) < 90:
                self.type = 'pink'
            else:
                self.type = 'icy'
            # self.type = choice(['pink', 'snowy'])
        if self.game.score >= PLAT_SNOW_START:
            self.type = choice(['icy', 'snowy'])

        # Platform images attachment
        if self.type == 'normal':
            self.image = random.choice(normal_images)
        elif self.type == 'wooden':
            self.image = random.choice(wood_images)
        elif self.type == 'sand':
            self.image = random.choice(sand_images)
        elif self.type == 'stone':
            self.image = random.choice(stone_images)
        elif self.type == 'pink':
            self.image = random.choice(pink_images)
        elif self.type == 'snowy':
            self.image = random.choice(snowy_images)
        elif self.type == 'icy':
            self.image = random.choice(icy_images)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Applying the sprites spawning on platform if wing pow is not initiated
        if not self.game.player.has_wings:
            if random.randrange(100) < POW_SPAWN_RATIO and not game.player.has_bubble and not game.player.has_jetpack \
                    and len(self.game.powerups) == 0 and self.game.score != 0 and not self.on_move_y:
                Powerup(self.game, self)
                self.has_pow = True
            if random.randrange(100) < COIN_SPAWN_RATIO:
                Coin(self.game, self)
                self.has_coin = True
            # There shouldn't be 2 much mobs
            if len(self.game.mobs) < 3:
                if random.randrange(100) < SPIKEY_SPAWN_RATIO and self.image == normal_images[0] and not self.on_move \
                        and not self.has_mob and PLAT_SNOW_START > self.game.score > SPIKEY_SPAWN_SCORE:
                    Spikey(self.game, self)
                    self.has_spikey = True
                    self.has_mob = True
                if random.randrange(100) < CLOUD_SPAWN_RATIO and not self.on_move and not self.has_mob and \
                        self.game.score > PLAT_STONE_START:
                    Cloud(self.game, self)
                    self.has_cloud = True
                    self.has_mob = True
                if random.randrange(100) < WM_SPAWN_RATIO and (self.image == pink_images[0] or self.image == snowy_images[0]) and not self.on_move \
                        and not self.has_mob and self.game.score > PLAT_PINK_START:
                    Wingman(self.game, self)
                    self.has_wingman = True
                    self.has_mob = True

    def update(self, *args):
        # Moving left/right
        if self.on_move_x:
            self.rect.x += self.vel_x
            if self.rect.right > WIDTH - 15:
                self.vel_x = -1
            if self.rect.left < 15:
                self.vel_x = 1
        # Moving up/down
        if self.on_move_y:
            self.rect.y += self.vel_y
            self.count_vel_y += self.vel_y
            if self.count_vel_y > 130:
                self.vel_y = -1
            if self.count_vel_y < 0:
                self.vel_y = 1


class Powerup(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        # We define the type as boost and then we change it if needed
        self.type = 'boost'
        self.spawn_score = 0
        self.spawn_ratio = random.randrange(100)
        if 20 < self.spawn_ratio < 50:
            self.type = 'bubble'
        elif 7 < self.spawn_ratio < 20:
            self.type = 'wings'
        elif 0 < self.spawn_ratio < 7:
            self.type = 'jetpack'
        if self.type == 'boost':
            self.image = self.game.spritesheet1.get_image(820, 1805, 71, 70)
        elif self.type == 'bubble':
            self.image = self.game.spritesheet1.get_image(826, 134, 71, 70)
        elif self.type == 'jetpack':
            self.image = self.game.spritesheet1.get_image(852, 1089, 65, 77)
        elif self.type == 'wings':
            self.image = self.game.spritesheet1.get_image(826, 1292, 71, 70)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # Position of the pow
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 2
        # Jumping var
        self.jumpCount = 1.2

    def update(self):
        self.rect.centerx = self.plat.rect.centerx
        # Jetpack does not jump
        if self.type != 'jetpack':
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
        # Jetpack always is still
        else:
            self.rect.bottom = self.plat.rect.top
        # Killing the sprite
        if not self.game.platforms.has(self.plat):
            self.kill()
            self.plat.has_pow = False


class Coin(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = POW_LAYER
        self.groups = game.all_sprites, game.coins
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        # Animation properties
        self.last_update = 0
        self.current_frame = 0
        self.load_images()
        self.image = self.gold_images[0]
        self.rect = self.image.get_rect()
        # Position
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        # Images depending on the score
        if PLAT_STONE_START > self.game.score >= 0:
            self.type = 'bronze'
        elif PLAT_PINK_START > self.game.score > PLAT_STONE_START:
            self.type = 'silver'
        else:
            self.type = 'gold'

    def load_images(self):
        self.gold_images = [self.game.spritesheet1.get_image(698, 1931, 84, 84),
                            self.game.spritesheet1.get_image(829, 0, 66, 84),
                            self.game.spritesheet1.get_image(897, 1574, 50, 84),
                            self.game.spritesheet1.get_image(645, 651, 15, 84),
                            pygame.transform.flip(self.game.spritesheet1.get_image(897, 1574, 50, 84), True, False),
                            pygame.transform.flip(self.game.spritesheet1.get_image(829, 0, 66, 84), True, False)]
        for image in self.gold_images:
            image.set_colorkey(BLACK)
        self.silver_images = [self.game.spritesheet1.get_image(584, 406, 84, 84),
                              self.game.spritesheet1.get_image(852, 1003, 66, 84),
                              self.game.spritesheet1.get_image(899, 1219, 50, 84),
                              self.game.spritesheet1.get_image(662, 651, 14, 84),
                              pygame.transform.flip(self.game.spritesheet1.get_image(899, 1219, 50, 84), True, False),
                              pygame.transform.flip(self.game.spritesheet1.get_image(852, 1003, 66, 84), True, False)]
        for image in self.silver_images:
            image.set_colorkey(BLACK)
        self.bronze_images = [self.game.spritesheet1.get_image(707, 296, 84, 84),
                              self.game.spritesheet1.get_image(826, 206, 66, 84),
                              self.game.spritesheet1.get_image(899, 116, 50, 84),
                              self.game.spritesheet1.get_image(670, 406, 14, 84),
                              pygame.transform.flip(self.game.spritesheet1.get_image(899, 116, 50, 84), True, False),
                              pygame.transform.flip(self.game.spritesheet1.get_image(826, 206, 66, 84), True, False)]
        for image in self.bronze_images:
            image.set_colorkey(BLACK)

    def update(self):
        time_passed = pygame.time.get_ticks()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 5
        if time_passed - self.last_update > 100:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.gold_images)
            if self.type == 'bronze':
                self.image = self.bronze_images[self.current_frame]
            elif self.type == 'silver':
                self.image = self.silver_images[self.current_frame]
            else:
                self.image = self.gold_images[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.centerx = self.plat.rect.centerx
            self.rect.bottom = self.plat.rect.top - 5
        # We kill the sprite when the plat is killed
        if not self.game.platforms.has(self.plat):
            self.kill()
            self.plat.has_coin = False


class Flyman(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Images and animation
        self.image_up = self.game.spritesheet1.get_image(566, 510, 122, 139)
        self.image_up.set_colorkey(BLACK)
        self.image_down = self.game.spritesheet1.get_image(568, 1534, 122, 135)
        self.image_down.set_colorkey(BLACK)
        self.image = self.image_up
        self.rect = self.image.get_rect()
        # Position
        self.rect.centerx = random.choice([-100, WIDTH + 100])
        self.rect.y = HEIGHT / 3
        # Move properties
        self.velx = random.randrange(1, 4)
        self.vely = 0
        self.dy = 0.5

    def update(self):
        # We apply movement
        self.rect.x += self.velx
        self.vely += self.dy
        self.rect.y += self.vely
        # We apply up and down movement
        if self.vely > 3 or self.vely < -3:
            self.dy *= -1
        rect_center = self.rect.center
        # We apply animation
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = rect_center
        # The sprite moves left and right until it is off HEIGHT
        if self.rect.left > WIDTH + 100 or self.rect.right < -100:
            self.velx *= -1
        # Killing the sprite
        if self.rect.centery > HEIGHT + 100:
            self.game.has_flyman = False
            self.kill()


class CloudBG(pygame.sprite.Sprite):
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
        self.rect.y = random.randrange(-500, -50)

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
        self.acc_x = SPIKEY_ACC
        self.facing_left = False
        self.facing_right = True

    def load_images(self):
        self.images_R = [self.game.spritesheet1.get_image(704, 1256, 120, 159),
                         self.game.spritesheet1.get_image(812, 296, 90, 155)]
        for image in self.images_R:
            image.set_colorkey(BLACK)

        self.images_L = [pygame.transform.flip(self.game.spritesheet1.get_image(704, 1256, 120, 159), True, False),
                         pygame.transform.flip(self.game.spritesheet1.get_image(812, 296, 90, 155), True, False)]
        for image in self.images_L:
            image.set_colorkey(BLACK)

    def update(self):
        self.animation()
        if self.game.platforms.has(self.plat):
            self.rect.bottom = self.plat.rect.top - 1
        # Applying constant movement
        if self.facing_left or self.facing_right:
            self.rect.x += self.acc_x
        # Moving from right to left
        if self.rect.right > self.plat.rect.right:
            self.facing_right = False
            self.facing_left = True
            self.acc_x = -SPIKEY_ACC
        # Moving from left to right
        if self.rect.left < self.plat.rect.left:
            self.facing_right = True
            self.facing_left = False
            self.acc_x = SPIKEY_ACC
        # Killing the sprite when it disappears off the screen
        if self.rect.top > HEIGHT:
            self.kill()
            self.plat.has_spikey = False
            self.plat.has_mob = False

    def animation(self):
        time_passed = pygame.time.get_ticks()
        if time_passed - self.last_update > SPIKEY_FRAME_TIME:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.images_R)
            rect_bottom = self.rect.bottom
            centerx = self.rect.centerx
            if self.facing_right:
                self.image = self.images_R[self.current_frame]
                self.rect.x += self.acc_x
            if self.facing_left:
                self.image = self.images_L[self.current_frame]
                self.rect.x += self.acc_x
            self.rect = self.image.get_rect()
            self.rect.centerx = centerx
            self.rect.bottom = rect_bottom


class Cloud(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = 4
        self.groups = game.all_sprites, game.passive_mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        # Defining the images
        self.images = [self.game.spritesheet1.get_image(0, 1152, 260, 134),
                       Get_image_res(pygame.image.load('graphics/Cloud1.png'), 2),
                       Get_image_res(pygame.image.load('graphics/Cloud2.png'), 2),
                       Get_image_res(pygame.image.load('graphics/Cloud3.png'), 2),
                       Get_image_res(pygame.image.load('graphics/Cloud4.png'), 2)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top - 60
        self.last_update = 0
        self.last_struck = False
        self.current_frame = 0
        # The first image is from the spritesheet so we set the colorkey to black
        if self.image == self.images[0]:
            self.image.set_colorkey(BLACK)

    def update(self, *args):
        self.rect.centerx = self.plat.rect.centerx
        if self.game.platforms.has(self.plat):
            self.rect.bottom = self.plat.rect.top - 60
        # Setting the animation
        time_passed = pygame.time.get_ticks()
        if time_passed - self.last_update > 500:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
        # Spawning the lightining at the peak image
        if self.image == self.images[4] and len(self.game.lightinings) < 4:
            Lightining(self.game, self)
        # Killing the sprite when it dissapears off the screen
        if self.rect.top > HEIGHT:
            self.kill()
            self.plat.has_cloud = False
            self.plat.has_mob = False


# Spawns ony with a cloud
class Lightining(pygame.sprite.Sprite):
    def __init__(self, game, cloud):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs, game.lightinings
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cloud = cloud
        self.image = self.game.spritesheet1.get_image(895, 453, 55, 114)
        # Rare gold lightining
        if random.randrange(100.0) < 1.5:
            self.image = self.game.spritesheet1.get_image(897, 0, 55, 114)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.top = self.cloud.rect.bottom - 2
        self.rect.centerx = self.cloud.rect.centerx - 5

    def update(self, *args):
        # Kill if the peak image is gone
        if self.cloud.image != self.cloud.images[4] or self.rect.top > HEIGHT:
            self.kill()


class Wingman(pygame.sprite.Sprite):
    def __init__(self, game, plat):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.flying_mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.images = [self.game.spritesheet1.get_image(382, 635, 174, 126),
                       self.game.spritesheet1.get_image(0, 1879, 206, 107),
                       self.game.spritesheet1.get_image(0, 1559, 216, 101),
                       self.game.spritesheet1.get_image(0, 1456, 216, 101),
                       self.game.spritesheet1.get_image(382, 510, 182, 123),
                       self.game.spritesheet1.get_image(0, 1456, 216, 101),
                       self.game.spritesheet1.get_image(0, 1559, 216, 101),
                       self.game.spritesheet1.get_image(0, 1879, 206, 107)]
        for image in self.images:
            image.set_colorkey(BLACK)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.centery = self.plat.rect.centery
        # Move properties
        self.acc_y = WM_ACC_UP
        self.vel_y = 0
        self.current_frame = 0
        self.last_update = 0
        self.facing_up = True
        self.facing_down = False

    def update(self, *args):
        self.animation()
        self.rect.centerx = self.plat.rect.centerx
        # We apply constant movement
        if self.facing_up or self.facing_down:
            self.rect.top += self.acc_y
            self.acc_y += self.vel_y
        # We apply the borders and change the animation properties
        # Going up
        if self.rect.y > self.plat.rect.y + 80:
            self.acc_y = WM_ACC_UP
            self.vel_y = 0
            self.facing_up = True
            self.facing_down = False
            self.current_frame = 0
        # We slow down the falling sprite to make it look more natural
        if self.plat.rect.y + 80 > self.rect.y > self.plat.rect.y + 40 and self.facing_down:
            self.vel_y = -WM_VEL
        # We fall and we speed up as we do it
        if self.rect.y < self.plat.rect.y - 120:
            self.acc_y = WM_ACC_DOWN
            self.vel_y = WM_VEL
            if self.acc_y >= 4:
                self.acc_y = 4
            self.facing_down = True
            self.facing_up = False
        # Killing the sprite when it is out of the screen
        if not self.game.platforms.has(self.plat):
            if self.rect.y > HEIGHT:
                self.kill()
                self.plat.has_wingman = False
                self.plat.has_mob = False

    def animation(self):
        # Animation up and down
        time_passed = pygame.time.get_ticks()
        if self.facing_up:
            if time_passed - self.last_update > WM_FRAME_TIME:
                self.last_update = time_passed
                self.current_frame = (self.current_frame + 1) % len(self.images)
                centery = self.rect.centery
                self.image = self.images[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.centery = centery
        else:
            self.image = pygame.transform.flip(self.images[4], False, True)


class Sun(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.flying_mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Applying sun types according to the score
        self.type = 'sun'
        if 1500 > self.game.score > SUN_SPAWN_SCORE:
            self.type = 'moon'
        if self.type == 'sun':
            self.images = [self.game.spritesheet1.get_image(534, 913, 142, 148),
                           self.game.spritesheet1.get_image(421, 1390, 148, 142)]
        elif self.type == 'moon':
            self.images = [self.game.spritesheet1.get_image(534, 763, 142, 148),
                           self.game.spritesheet1.get_image(464, 1122, 148, 141)]
        for image in self.images:
            image.set_colorkey(BLACK)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        # Applying y and x pos
        if self.game.player.has_wings:
            self.rect.centerx = random.randrange(70, WIDTH - 70)
        else:
            self.rect.centerx = random.choice([-100, WIDTH + 100])
        self.rect.y = random.choice([-100, -75])
        # The vel is so that when everything gets moved to the bottom our sun moves slower to make the game challenging
        # The vel isn't found anywhere in the class.It is in the game in flying mobs
        self.vel_y = -PLAYER_JUMP_V // 3.5
        self.vel_x = SUN_VEL
        self.current_frame = 0
        self.last_update = 0

    def update(self, *args):
        # Apply animation
        self.animation()
        if self.game.player.has_wings:
            self.vel_y = 0
        else:
            # Apply constant movement
            self.rect.x += self.vel_x
            # Changing the direction
            if self.rect.right > WIDTH - 5:
                self.vel_x = -SUN_VEL
            if self.rect.left < 5:
                self.vel_x = SUN_VEL
        # Killing the sprite if it is off the screen
        if self.rect.y > HEIGHT:
            self.kill()
            self.game.has_sun = False

    def animation(self):
        time_passed = pygame.time.get_ticks()
        if time_passed - self.last_update > SUN_FRAME_CHANGE:
            self.last_update = time_passed
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]

