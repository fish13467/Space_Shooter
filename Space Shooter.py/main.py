### Imports ###
import pathlib
import sys
from random import choice, randint
from time import sleep


import pygame as pg
pg.init()

### Data ###
game_over = False
delta_time = 0

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

SPRITE_WIDTH = 40
SPRITE_HEIGHT = 40

POWER_RATE = 15 # Seconds between possible pu drops
power_timer = POWER_RATE

FPS = 60

WORK_DIR = pathlib.Path.cwd()

## fonts 
LARGE_FONT = pg.font.Font(WORK_DIR/'assets'/'game_font.ttf', 30)
SMALL_FONT = pg.font.Font(WORK_DIR/'assets'/'game_font.ttf', 16)


### paths
BG_IMG_PATH = WORK_DIR/"assets"/"UI"/"space_background.png"
BG_IMG = pg.transform.scale(pg.image.load(BG_IMG_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT))

PLAYER_IMG_PATH = WORK_DIR/"assets"/"Players"/"playerShip3_orange.png"

ENEMY_IMG_PATH_1 = WORK_DIR/"assets"/"Enemies"/"enemyBlack1.png"
ENEMY_IMG_PATH_2 = WORK_DIR/"assets"/"Enemies"/"enemyBlack2.png"
ENEMY_IMG_PATH_3 = WORK_DIR/"assets"/"Enemies"/"enemyBlack3.png"
ENEMY_IMG_PATH_4 = WORK_DIR/"assets"/"Enemies"/"enemyBlack4.png"
ENEMY_IMG_PATH_5 = WORK_DIR/"assets"/"Enemies"/"enemyBlack5.png"

LASER_IMG_PATH = WORK_DIR/"assets"/"Lasers"/"LaserGreen11.png"

METEOR_IMG_PATH_1 = WORK_DIR/"assets"/"Meteors"/"meteorBrown_med1.png"
METEOR_IMG_PATH_2 = WORK_DIR/"assets"/"Meteors"/"meteorBrown_med3.png"
METEOR_IMG_PATH_3 = WORK_DIR/"assets"/"Meteors"/"meteorGrey_small1.png"
METEOR_IMG_PATH_4 = WORK_DIR/"assets"/"Meteors"/"meteorGrey_small2.png"
METEOR_IMG_PATH_5 = WORK_DIR/"assets"/"Meteors"/"meteorGrey_tiny1.png"
METEOR_IMG_PATH_6 = WORK_DIR/"assets"/"Meteors"/"meteorBrown_tiny2.png"


LASER_SFX_PATH = WORK_DIR/"assets"/"Audio"/"laserSmall_002.ogg"
EXPLOSION_SFX_PATH = WORK_DIR/"assets"/"Audio"/"explosionCrunch_000.ogg"


HP_IMG_PATH = WORK_DIR/"assets"/"Power-ups"/"pill_red.png"
FR_IMG_PATH = WORK_DIR/"assets"/"Power-ups"/"bolt_gold.png"

ENEMY_IMG_PATHS = (
    ENEMY_IMG_PATH_1, ENEMY_IMG_PATH_3, ENEMY_IMG_PATH_2, 
    ENEMY_IMG_PATH_4, ENEMY_IMG_PATH_5
)

METEOR_IMG_PATHS = (
    METEOR_IMG_PATH_1, METEOR_IMG_PATH_2, METEOR_IMG_PATH_3, 
   METEOR_IMG_PATH_4, METEOR_IMG_PATH_5, METEOR_IMG_PATH_6
)

### Window Setup ###



mw = pg.display.set_mode((SCREEN_HEIGHT, SCREEN_WIDTH))
pg.display.set_caption("Space Shooter")
clock = pg.time.Clock()


### Classes ###
class BaseSprite(pg.sprite.Sprite):
    def __init__(self, img_path,scale_w, scale_h, x_pos, y_pos, step):
        super().__init__()
        if scale_w is not None and scale_h is not None:
            self.image = pg.transform.scale(pg.image.load(img_path), (scale_w, scale_h))
        else:
            self.image = pg.image.load(img_path)

        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.step = step
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class PlayerSprite(BaseSprite):
    def __init__(self, img_path, scale_w, scale_h, x_pos, y_pos, step):
        super().__init__(img_path, scale_w, scale_h, x_pos, y_pos, step)
        self.start_x = x_pos
        self.start_y = y_pos

        self.lives = 3
        self.score = 0

        self.FIRE_RATE = 0.1
        self.shot_timer = self.FIRE_RATE
        self.fr_pu_timer = None

    def update(self):
        pressed_keys = pg.key.get_pressed()

        if pressed_keys[pg.K_a] and self.rect.x >= 0: 
            self.rect.x -= self.step

        if pressed_keys[pg.K_d] and self.rect.x <= SCREEN_WIDTH - SPRITE_WIDTH:
            self.rect.x += self.step

        
        self.shot_timer -= delta_time
        if pressed_keys[pg.K_SPACE] and self.shot_timer <= 0:
            laser_sfx.play()
            self.shot_timer = self.FIRE_RATE
            laser = LaserSprite(LASER_IMG_PATH, 6, 36, self.rect.centerx - 3, self.rect.y -20, 4)
            laser_sprite_group.add(laser)

        if self.FIRE_RATE != 0.5:
            if self.fr_pu_timer is None: 
                self.fr_pu_timer = pg.time.get_ticks()

            elif pg.time.get_ticks() - self.fr_pu_timer >= 8000:
                self.FIRE_RATE = 0.5
                self.fr_pu_timer = None
        
class LaserSprite(BaseSprite):
    def update(self):
        if self.rect.y >= self.rect.height:
            self.rect.y -= self.step
            if pg.sprite.groupcollide(laser_sprite_group, enemy_sprite_group, True, True):
                explosion_sfx.play()
                player.score += 10
                del self

        else: 
            laser_sprite_group.remove(self)
            del self
class EnemySprite(BaseSprite):

    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, enemy_sprite_group, True):
                explosion_sfx.play()
                player.lives -= 1
                del self

        else:
            enemy_sprite_group.remove(self)
            player.lives -= 1
            del self
        
class MeteorSprite(BaseSprite):
    def update(self): 
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.groupcollide(player_sprite_group, meteor_sprite_group, True, True):
                explosion_sfx.play()
                del self 
                player.lives = 0
       
            if pg.sprite.groupcollide(enemy_sprite_group, meteor_sprite_group, True, True):
                explosion_sfx.play()
                del self 
                
        
        else:
            meteor_sprite_group.remove(self)
            del self

class HPPowerSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, pu_sprite_group, True):
                del self
                if player.lives < 4:
                    player.lives += 1


        else:
            pu_sprite_group.remove(self)
            del self

class FRPowerSprite(BaseSprite):
     def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, pu_sprite_group, True):
                del self
                player.FIRE_RATE = 0.2

        else:
            
            pu_sprite_group.remove(self)
            del self


### Functions ##
def check_quit(event):
    if event.type == pg.QUIT:
        pg.quit()
        sys.exit()

def spawn_enemies():
    if len(enemy_sprite_group) < 5:
        enemy = EnemySprite(
          choice(ENEMY_IMG_PATHS), 
          SPRITE_WIDTH, SPRITE_HEIGHT,
          randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
          -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
          randint(1, 2)
        )
        enemy_sprite_group.add(enemy)

def spawn_meteors():
    if len(meteor_sprite_group) < 2:
        meteor = MeteorSprite(
          choice(METEOR_IMG_PATHS), 
          None, None,
          randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
          -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
          randint(2, 4)
        )

        meteor_sprite_group.add(meteor)
def spawn_power(POWER_RATE, power_timer, delta_time):
    power_timer -= delta_time
    if power_timer <= 0:
        power_timer = POWER_RATE
        spawn = bool(randint(0, 1))
        if spawn:
            power_type = bool(randint(0, 1))
            if power_type: # True = HP, 
                power_up = HPPowerSprite(
                    HP_IMG_PATH, 
                    None, None, 
                    randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                    -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                    randint(2, 4)
                )
                pu_sprite_group.add(power_up)                       

            elif not power_type: # false = fr
                 power_type = bool(randint(0, 1))
            if power_type:
                power_up = FRPowerSprite(
                    FR_IMG_PATH, 
                    None, None, 
                    randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                    -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                    randint(2, 4)
                )
                pu_sprite_group.add(power_up)

    return power_timer


def draw_score():
    score_image = SMALL_FONT.render(f"Score: {player.score}", True, (214, 214, 214))
    mw.blit(score_image, (15, 10))

def draw_lives():
    lives_image = SMALL_FONT.render(f"{player.lives} Lives ", True, (214, 214, 214))
    mw.blit(lives_image, (600, 10))

def check_game_over():
    if player.lives <= 0:
        txt_img_1 = LARGE_FONT.render("Game Over!", True, (214, 214, 214))
        txt_img_2 = LARGE_FONT.render("Score:", True, (214, 214, 214))
        txt_img_3 = LARGE_FONT.render(f"{player.score}", True, (214, 214, 214))
    

        txt_rect_1 = txt_img_1.get_rect()
        txt_rect_2 = txt_img_2.get_rect()
        txt_rect_3 = txt_img_3.get_rect()


        txt_rect_1.center = (SCREEN_WIDTH/2, 340)
        txt_rect_2.center = (SCREEN_WIDTH/2, 390)
        txt_rect_3.center = (SCREEN_WIDTH/2, 440)


        mw.blit(txt_img_1, txt_rect_1)
        mw.blit(txt_img_2, txt_rect_2)
        mw.blit(txt_img_3, txt_rect_3)


        pg.display.flip()
        sleep(2)
        pg.quit()
        sys.exit()

### Sprite & Groups ###
player_sprite_group = pg.sprite.Group()
enemy_sprite_group = pg.sprite.Group()
laser_sprite_group = pg.sprite.Group()
meteor_sprite_group = pg.sprite.Group()
pu_sprite_group = pg.sprite.Group()
## Sprites
player = PlayerSprite(PLAYER_IMG_PATH, SPRITE_WIDTH, SPRITE_HEIGHT, 360, 650, 5)

## Adding Sprites to Groups
player_sprite_group.add(player)


## SFX
laser_sfx = pg.mixer.Sound(LASER_SFX_PATH)
explosion_sfx = pg.mixer.Sound(EXPLOSION_SFX_PATH)

### Game Loop ###
while not game_over:
    mw.blit(BG_IMG, (0, 0))

    spawn_enemies()
    spawn_meteors()
    power_timer = spawn_power(POWER_RATE, power_timer, delta_time)

    check_game_over()
    draw_score()
    draw_lives()


    player_sprite_group.update()
    enemy_sprite_group.update()
    laser_sprite_group.update()
    meteor_sprite_group.update()
    pu_sprite_group.update()


    player_sprite_group.draw(mw)
    enemy_sprite_group.draw(mw)
    laser_sprite_group.draw(mw)
    meteor_sprite_group.draw(mw)
    pu_sprite_group.draw(mw)
    
    

    for event in pg.event.get():
        check_quit(event)

    pg.display.flip()
    delta_time = clock.tick(FPS) / 1000