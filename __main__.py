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
                self.coin_count = int(f.read())
            except:
                self.coin_count = 0

        # Load spritesheet image
        self.spritesheet1 = Spritesheet1(path.join(self.dir, SPRITESHEET1))
        img_dir = path.join(self.dir, 'images')

        # Cloud images
        self.cloud_images = []
        for i in range(1,4):
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
        self.clouds = pygame.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
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
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

        # Spawn a mob?
        time_passed = pygame.time.get_ticks()
        if time_passed - self.mob_timer > MOB_FREQ + random.choice([-1000, -500, 0, 500, 1000]) and self.player.pos.y < HEIGHT - 50:
            self.mob_timer = time_passed
            Mob(self)

        # Hit mobs
        mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits and not self.player.invincible:
            if pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask):
                self.playing = False
        # Bubble mechanics
        if self.player.invincible:
            self.player.vel.y = -BUBBLE_POWER
            if self.score_inv >= 150:
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
                        if lowest_plat.type == 'snowy':
                            self.player.friction = PLAYER_FRICTION_ON_SNOW
                        else:
                            self.player.friction = PLAYER_FRICTION


        # if player reaches the 1/4 of the screen
        if self.player.rect.top <= HEIGHT / 3:
            if random.randrange(100) < CLOUD_BG_SPAWN_RATIO:
                Cloud_bg(self)
            self.player.pos.y += max(abs(self.player.vel.y), 3)
            # Move the clouds further down
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 1.5)
            # Move the platforms further down
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 3)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
                    # We add value to this score so we can monitor the bubble
                    if self.player.invincible:
                        self.score_inv += 10
            # Move the powerups further down(code differs because their vel is always changing)
            for pow in self.powerups:
                pow.rect.y += max(abs(self.player.vel.y), 3) + pow.jumpCount
            # Move the mobs further down
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 3)
            for passive_mob in self.passive_mobs:
                passive_mob.rect.y += max(abs(self.player.vel.y), 3)




        # Player/Coin hits
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        if coin_hits:
            self.coin_count += 1

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
            plat = Platform(self, random.randrange(3, WIDTH - p_width),
                         random.randrange(-75, -30))
            # If the platform is beyond the screen we adjust it's pos
            if plat.rect.right > WIDTH:
                plat.rect.right = WIDTH - 5
            elif plat.rect.left < 0:
                plat.rect.left = 5
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
        if 250 > self.score >= 0:
            self.screen.fill(BG_COLOR)
        if 500 > self.score >= 250:
            self.screen.fill(BG_COLOR)
        if 750 > self.score >= 500:
            self.screen.fill((140, 156, 166))
        if 1000 > self.score >= 750:
            self.screen.fill((215, 122, 255))
        if self.score >= 1000:
            self.screen.fill((215, 222, 255))
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 32, BLACK, WIDTH / 2, 15)
        self.draw_text('Coins: ' + str(self.coin_count), 32, BLACK, 50, 15)
        # *after* drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        #pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        #pygame.mixer.music.play(loops=-1)
        self.screen.fill(BG_COLOR)
        self.draw_text(TITLE, 68, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('A/D to move, W to jump', 32, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play', 32, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text('High score :' + str(self.highscore), 32, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        #pygame.mixer.music.load(path.join(self.sound_dir, 'Yippee.ogg'))
        #pygame.mixer.music.play(loops=-1)
        self.screen.fill(BG_COLOR)
        self.draw_text('GAME OVER', 68, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text('Score :' + str(self.score), 32, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text('Press a key to play again', 32, WHITE, WIDTH / 2, HEIGHT * 3 / 4)

        # Draw the highscore count
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text('New high score!', 32, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, SAVES_FILE), 'w',) as f:
                f.write(str(self.score))
        else:
            self.draw_text('High score :' + str(self.highscore), 32, WHITE, WIDTH / 2, HEIGHT / 2 + 40)

        with open(path.join(self.dir, COIN_FILE), 'w',) as f:
            f.write(str(self.coin_count))

        # Draw the coin count
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)



    """def fade(self, WIDTH, HEIGHT):
        screen = pygame.Surface((WIDTH, HEIGHT))
        screen.fill((255, 68, 248))
        for alpha in range(0, 300):
            screen.set_alpha(alpha)
            self.draw()
            self.screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.time.delay(5)"""


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()