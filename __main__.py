# My game
# Sound and Music
# Art from Kenney.nl
# Happy Tune by http://opengameart.org/users/syncopika
# Yippee by http://opengameart.org/users/snabisch

import pygame
import random
from settings import *
from Sprites import *
from os import path

class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font(FONT_NAME)
        self.menu = pygame.sprite.Group()
        self.load_data()

    def load_data(self):
        # Load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, SAVES_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        with open(path.join(self.dir, COIN_FILE), 'r') as f:
            try:
                self.coin_amount = int(f.read())
            except:
                self.coin_amount = 0

        # Load spritesheet image
        self.spritesheet1 = Spritesheet1(path.join(self.dir, SPRITESHEET1))
        img_dir = path.join(self.dir, 'images')
        # Bg images
        self.bg_menu = pygame.image.load('bg_menu.png')
        self.bg_menu1 = pygame.image.load('bg_menu1.png')
        # Button images
        self.menu_b1 = Button(self, WIDTH // 2, HEIGHT // 2 + 56)
        self.menu_b2 = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 2)
        self.menu_b3 = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 3)
        self.tut_b = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 3)
        # Cloud images
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pygame.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
        # Load Sound
        self.sound_dir = path.join(self.dir, 'Sounds')
        self.jump_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'Jump33.wav'))
        self.boost_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'Boost16.wav'))

    def new(self):
        # start a new game
        self.score = 0
        self.score_inv = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.passive_mobs = pygame.sprite.Group()
        self.flying_mobs = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        self.has_flyman = False
        # Fade properties
        self.R = 136
        self.G = 202
        self.B = 255
        self.first_fade = False
        self.second_fade = False
        self.third_fade = False
        self.color_change = False
        # Music
        pygame.mixer.music.load(path.join(self.sound_dir, 'Happy Tune.ogg'))
        for i in range(10):
            c = Cloud_bg(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # Game Loop
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()

        pygame.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.draw()
        self.all_sprites.update()


        # Spawn a mob?
        time_passed = pygame.time.get_ticks()
        if time_passed - self.mob_timer > MOB_FREQ + random.choice([-1000, -500, 0, 500, 1000]) and self.player.pos.y < HEIGHT - 50 and not self.has_flyman:
            self.mob_timer = time_passed
            Flyman(self)
            self.has_flyman = True

        # Hit mobs
        mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits and not self.player.invincible:
            if pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask):
                self.playing = False
        # Hit flying mobs
        f_mob_hits = pygame.sprite.spritecollide(self.player, self.flying_mobs, False)
        if f_mob_hits and not self.player.invincible:
            if pygame.sprite.spritecollide(self.player, self.flying_mobs, False, pygame.sprite.collide_mask):
                self.playing = False
        # Bubble mechanics
        if self.player.invincible:
            self.player.vel.y = -BUBBLE_POWER
            if self.score_inv >= 180:
                self.player.invincible = False

        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest_plat = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest_plat.rect.bottom:
                        lowest_plat = hit

                if lowest_plat.rect.left - 10 < self.player.pos.x < lowest_plat.rect.right + 10:
                    if self.player.pos.y < lowest_plat.rect.centery - 3:
                        self.player.pos.y = lowest_plat.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False
                        # If it is the snow platform then we change the friction
                        if lowest_plat.type == 'icy':
                            self.player.friction = PLAYER_FRICTION_ON_SNOW
                        else:
                            self.player.friction = PLAYER_FRICTION

        # If player reaches the 1/4 of the screen
        if self.player.rect.top <= HEIGHT / 2 - 80:
            if random.randrange(100) < CLOUD_BG_SPAWN_RATIO:
                Cloud_bg(self)
            self.player.pos.y += max(abs(self.player.vel.y), 3)
            # Move the clouds further down
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 1.5)
            # Move the platforms further down
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 3)
                if plat.rect.top >= HEIGHT and not plat.has_spikey:
                    plat.kill()
                    self.score += random.randrange(10, 16)
                    # The variable at which we change fade
                    self.color_change = True
                    # We add value to this score so we can monitor the bubble
                    if self.player.invincible:
                        self.score_inv += 10

            # Move the powerups further down(code differs because their vel is always changing)
            for pow in self.powerups:
                pow.rect.y += max(abs(self.player.vel.y), 3) + pow.jumpCount
            # Move the mobs further down
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 3)
            for f_mob in self.flying_mobs:
                f_mob.rect.y += max(abs(self.player.vel.y), 3) + f_mob.vel_y
            for passive_mob in self.passive_mobs:
                passive_mob.rect.y += max(abs(self.player.vel.y), 3)

        # Player/Coin hits
        for coin in self.coins:
            coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
            if coin_hits:
                if coin.type == 'bronze':
                    self.coin_amount += 1
                elif coin.type == 'silver':
                    self.coin_amount += 3
                elif coin.type == 'gold':
                    self.coin_amount += 5

        # Player/Powerup hits
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in powerup_hits:
            if hit.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
            elif hit.type == 'bubble':
                self.player.invincible = True
                self.player.jumping = False
                self.score_inv = 0

        # DIE!!!!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep the game runnin'
        while len(self.platforms) < 6:
            p_width = random.randrange(50, 100)
            p = Platform(self, random.randrange(3, WIDTH - p_width),
                         random.randrange(-75, -30))
            # If platforms collide we move them up
            for plat in self.platforms:
                hit = pygame.sprite.spritecollide(p, self.platforms, False)
                if hit:
                    dist = abs(plat.rect.y - p.rect.y)
                    p.rect.y = -dist - 100
            # If the platform is beyond the screen we adjust it's pos
            if p.rect.right > WIDTH:
                p.rect.right = WIDTH - 5
            elif p.rect.left < 0:
                p.rect.left = 5
        # Fading the screen when the player hits some score
        #if self.score == 100:
            #self.fade(WIDTH, HEIGHT)


    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        # Screen color change
        self.fade()
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 32, BLACK, WIDTH / 2, 15)
        self.draw_text('Coins: ' + str(self.coin_amount), 32, BLACK, 50, 15)
        # *after* drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        #pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        #pygame.mixer.music.play(loops=-1)
        self.screen.blit(self.bg_menu, (0, 0))
        self.draw_text(TITLE, 68, ALMOST_WHITE, WIDTH / 2, HEIGHT / 4)
        self.menu.draw(self.screen)
        self.menu_b1.draw_txt('Play', 32, ALMOST_WHITE)
        self.menu_b2.draw_txt('Tutorial', 32, ALMOST_WHITE)
        self.menu_b3.draw_txt('Settings', 32, ALMOST_WHITE)
        self.draw_text('High score :' + str(self.highscore), 32, ALMOST_WHITE, WIDTH / 2, 15)

        def wait_for_key_startscr():
            pygame.mouse.set_visible(True)
            waiting = True
            while waiting:
                self.clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        self.running = False
                    # Getting the mouse pos and checking the button clicks
                    pos = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.menu_b1.rect.collidepoint(pos):
                            waiting = False
                            pygame.mouse.set_visible(False)
                        elif self.menu_b2.rect.collidepoint(pos):
                            self.show_tutorial_screen()
                        elif self.tut_b.rect.collidepoint(pos):
                            waiting = False
                            self.tut_b.kill()
                            self.show_start_screen()
        pygame.display.flip()
        wait_for_key_startscr()
        pygame.mixer.music.fadeout(500)

    def show_tutorial_screen(self):
        self.screen.blit(self.bg_menu, (0, 0))
        # Giving tutorial
        self.draw_text('Jumpy!', 72, ALMOST_WHITE, WIDTH / 2, HEIGHT / 10)
        self.draw_text('A/D to move, W to jump', 32, (0,102,133), WIDTH / 2, HEIGHT / 3)
        self.draw_text('Watch out for snowy platforms!', 32, (0,102,133), WIDTH / 2, HEIGHT / 3 + 36)
        self.draw_text('Collect coins and exchange them for goods!', 32, (0,102,133), WIDTH / 2, HEIGHT / 3 + 36 * 2)
        self.draw_text('Good Luck!:)', 32, (0,102,133), WIDTH / 2, HEIGHT / 2)
        # Creating a button
        self.tut_b = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 4)
        self.tut_b.draw_txt('Go back', 32, ALMOST_WHITE)
        pygame.display.flip()

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        #pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        #pygame.mixer.music.play(loops=-1)
        self.screen.blit(self.bg_menu, (0, 0))
        self.draw_text('GAME OVER', 68, ALMOST_WHITE, WIDTH / 2, HEIGHT / 5)
        self.draw_text('Score :' + str(self.score), 32, ALMOST_WHITE, WIDTH / 2, HEIGHT / 5 + 36)
        # Adjusting the buttons
        self.goscr_b1 = Button(self, WIDTH // 2, HEIGHT // 2 + 56)
        self.goscr_b2 = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 2)
        self.goscr_b3 = Button(self, WIDTH // 2, HEIGHT // 2 + 56 * 3)
        self.goscr_b1.draw_txt('Play again', 32, ALMOST_WHITE)
        self.goscr_b2.draw_txt('Return to menu', 32, ALMOST_WHITE)
        self.goscr_b3.draw_txt('Exit', 32, ALMOST_WHITE)
        # Draw the highscore count
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('New high score!', 32, ALMOST_WHITE, WIDTH / 2, HEIGHT / 5 + 36 * 2)
            with open(path.join(self.dir, SAVES_FILE), 'w',) as f:
                f.write(str(self.score))
        else:
            self.draw_text('High score :' + str(self.highscore), 32, ALMOST_WHITE, WIDTH / 2, HEIGHT / 5 + 36 * 2)

        with open(path.join(self.dir, COIN_FILE), 'w',) as f:
            f.write(str(self.coin_amount))

        def wait_for_key_goscr():
            pygame.mouse.set_visible(True)
            waiting = True
            while waiting:
                self.clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        self.running = False
                    # Getting the pos and checking the button clicks
                    pos = pygame.mouse.get_pos()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.goscr_b1.rect.collidepoint(pos):
                            waiting = False
                            pygame.mouse.set_visible(False)
                        if self.goscr_b2.rect.collidepoint(pos):
                            waiting = False
                            self.show_start_screen()
                        elif self.goscr_b3.rect.collidepoint(pos):
                            waiting = False
                            self.running = False
        # Draw the coin count
        pygame.display.flip()
        wait_for_key_goscr()
        pygame.mixer.music.fadeout(500)

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def fade(self):
        # Filling the screen with our start colour
        self.screen.fill((self.R, self.G, self.B))
        # slowly changing the start colour as platforms get killed
        if self.B > 169 and self.color_change and not self.first_fade and not self.second_fade:
            self.B -= 1
            if self.G > 169 and self.color_change:
                self.G -= 1
                self.color_change = False
            self.color_change = False
        self.screen.fill((self.R, self.G, self.B))
        # As we fill the first fade we set it to true so the first if statement is false
        if self.B == 169 and self.G == 169:
            self.first_fade = True
        # We can begin second fade now
        if self.R < 255 and self.color_change:
            self.R += 1
            if self.B < 255 and self.color_change :
                self.B += 1
                self.color_change = False
            self.color_change = False
        self.screen.fill((self.R, self.G, self.B))
        # Second fade is finished so we set it to true; 1st and 2nd ifs are false now
        if self.B == 255 and self.R == 255:
            self.second_fade = True
        # We begin the thind fade
        if self.G < 250 and self.color_change and self.second_fade and not self.third_fade:
            self.G += 1
            self.color_change = False
        # Third fade is finished so we set all the ifs to false now and stop the fade
        if self.G == 250:
            self.third_fade = True

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()