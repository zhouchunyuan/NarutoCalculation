import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
        def __init__(self):
                # initialize game window, etc
                pg.init()
                pg.mixer.init()
                pg.display.set_caption(TITLE)
                self.screen = pg.display.set_mode((WIDTH,HEIGHT))
                self.clock = pg.time.Clock()
                self.running = True
                self.font_name = pg.font.match_font(FONT_NAME)
                self.load_data()
                self.player_outlook = 'ninja_boy'

        def load_data(self):
                # load high score
                self.dir = path.dirname(__file__)
                img_dir = path.join(self.dir,'img')
                with open(path.join(self.dir,HS_FILE),'r') as f:
                        try:
                                self.highscore = int(f.read())
                        except:
                                self.highscore = 0
                # load spritesheet image
                self.spritesheet = Spritesheet(path.join(img_dir,SPRITESHEET))
                # cloud images
                self.cloud_images = []
                for i in range(1,9):
                        self.cloud_images.append(pg.image.load(path.join(img_dir,'cloud{}.png'.format(i))).convert())
                # load sounds
                self.snd_dir = path.join(self.dir,'snd')
                self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir,'Jump33.wav'))
                self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir,'Boost16.wav'))
                        
        def new(self):
                # start a new game
                
                self.score = 0
                self.all_sprites = pg.sprite.LayeredUpdates()
                self.platforms = pg.sprite.Group()
                self.powerups = pg.sprite.Group()
                self.mobs = pg.sprite.Group()
                self.clouds = pg.sprite.Group()
                self.player = Player(self,self.player_outlook)
                self.whiteboard = None
                self.active_platform = None
                for plat in PLATFORM_LIST:
                        Platform(self,plat[0],plat[1])
                self.mob_timer = 0
                pg.mixer.music.load(path.join(self.snd_dir,'Spectacle Carousel Loop.ogg'))
                self.run()
                
        def run(self):
                # Game loop
                pg.mixer.music.play(loops=-1)
                self.playing = True
                while self.playing:
                        self.clock.tick(FPS)
                        self.events()
                        self.update()
                        self.draw()
                pg.mixer.music.fadeout(500)
        def update(self):
                # Game loop - Update
                self.all_sprites.update()
                
                # spawn a mob ?
                now = pg.time.get_ticks()
                if now - self.mob_timer > MOB_FREQ + random.choice([-1000,-500,0,500,1000]):
                        self.mob_timer = now
                        Mob(self)
                # hit mobs ?
                mob_hits = pg.sprite.spritecollide(self.player,self.mobs,False,pg.sprite.collide_mask)
                if mob_hits:
                        self.playing = False
                # check if player hits a platform - only if falling
                if self.player.vel.y > 0:
                        hits = pg.sprite.spritecollide(self.player,self.platforms,False)
                        if hits:
                                lowest = hits[0]
                                for hit in hits:
                                        if hit.rect.bottom > lowest.rect.bottom:
                                                lowest = hit
                                if self.player.pos.x < lowest.rect.right + 10 and \
                                   self.player.pos.x > lowest.rect.left -10 :
                                        if self.player.pos.y < lowest.rect.centery:
                                                self.player.pos.y = lowest.rect.top
                                                self.player.vel.y = 0
                                                self.player.jumping = False
                                                self.active_platform = lowest

                # if player reaches top 1/4 screen
                if self.player.rect.top <= HEIGHT/4:
                        min_rolling_down_speed = 5
                        if random.randrange(100) < 10 and len(self.clouds)<5:
                                Cloud(self)
                        self.player.pos.y += max(abs(self.player.vel.y),min_rolling_down_speed)
                        for cloud in self.clouds:
                                cloud.rect.y += max(abs(self.player.vel.y/2),min_rolling_down_speed)
                        for mob in self.mobs:
                                mob.rect.y += max(abs(self.player.vel.y),min_rolling_down_speed)
                        for plat in self.platforms:
                                plat.rect.y += max(abs(self.player.vel.y),min_rolling_down_speed)
                                if plat.rect.top >= HEIGHT:
                                        plat.kill()
                                        self.score += 10
                # if player hits powerup
                pow_hits = pg.sprite.spritecollide(self.player,self.powerups,True)

                for pow in pow_hits:
                        if pow.type == 'boost':
                                self.boost_sound.play()
                                self.player.vel.y = -BOOST_POWER
                                self.player.jumping = False
                                
                # Die!
                if self.player.rect.bottom > HEIGHT:
                        for sprite in self.all_sprites:
                                sprite.rect.y -= max(self.player.vel.y,10)
                                if sprite.rect.bottom < 0:
                                        sprite.kill()
                        if len(self.platforms)==0:
                                self.playing = False
                # spawn new paltforms to keep some average number
                while len(self.platforms) < 6:
                        width = random.randrange(50,200)
                        Platform(self,random.randrange(0,WIDTH-width),
                                 random.randrange(-75,-30))
        def events(self):
                # Game loop - events
                for event in pg.event.get():
                        #check for closing window
                        if event.type == pg.QUIT:
                                if self.playing:
                                        self.playing = False
                                self.running = False

                        if event.type == pg.KEYUP:
                                if event.key ==pg.K_ESCAPE:
                                        self.playing = False
                                        self.running = False
                                        
                                # start to answer questions ?
                                if event.key >= pg.K_0 and event.key <=pg.K_9:
                                        if self.whiteboard is None :
                                                self.whiteboard = Whiteboard(self)
                                      
                                if event.key ==pg.K_RETURN:
                                        if self.whiteboard is None :
                                                self.whiteboard = Whiteboard(self)
                                        else:
                                                good_answer = self.active_platform.check_whiteboard_answer()
                                                if good_answer :
                                                        for mob in self.mobs.sprites():
                                                                mob.kill()
                                                        for plat in self.platforms.sprites():
                                                                y=plat.rect.top
                                                                x=plat.rect.centerx
                                                                if y < self.player.rect.bottom - 2:
                                                                        break
                                                        self.player.jump_to(x,y)
                                                        
                                                self.player.magic_on = not good_answer
                                                        
                                                self.whiteboard.kill()
                                                self.whiteboard = None
                       
                        if event.type == pg.KEYDOWN:
                                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                                        self.player.jump()
                                if event.key == pg.K_DOWN:
                                        self.player.lowdown = True

                        if event.type == pg.KEYUP:
                                if event.key == pg.K_SPACE or event.key == pg.K_UP:
                                        self.player.jump_cut()
                                if event.key == pg.K_DOWN:
                                        self.player.lowdown = False                            
                        if self.whiteboard is not None:
                                self.calculator(self.whiteboard,event)
                                
                        self.music_volume_event(event)
                        
        def music_volume_event(self,event):
                volume = pg.mixer.music.get_volume()
                if event.type == pg.KEYUP:
                        if event.key == pg.K_m:
                                if volume == 0:
                                        volume = 0.5
                                else:
                                        volume = 0
                pg.mixer.music.set_volume(volume)
        def calculator(self,whiteboard,event):
                if event.type == pg.KEYUP:
                        if   event.key == pg.K_0 : whiteboard.text += '0'
                        elif event.key == pg.K_1 : whiteboard.text += '1'
                        elif event.key == pg.K_2 : whiteboard.text += '2'
                        elif event.key == pg.K_3 : whiteboard.text += '3'
                        elif event.key == pg.K_4 : whiteboard.text += '4'
                        elif event.key == pg.K_5 : whiteboard.text += '5'
                        elif event.key == pg.K_6 : whiteboard.text += '6'
                        elif event.key == pg.K_7 : whiteboard.text += '7'
                        elif event.key == pg.K_8 : whiteboard.text += '8'
                        elif event.key == pg.K_9 : whiteboard.text += '9'
                        elif event.key == pg.K_BACKSPACE: whiteboard.text = whiteboard.text[:-1]
                         
        def draw(self):
                # Game loop - draw
                self.screen.fill(BGCOLOR)
                self.all_sprites.draw(self.screen)
                self.draw_text(str(self.score),30,RED,WIDTH/2,15)
                pg.display.flip()
                
        def show_start_screen(self):
                # game splash/start screen
                pg.mixer.music.load(path.join(self.snd_dir,'tensesituations.ogg'))
                pg.mixer.music.play(loops=-1)
                self.screen.fill(BGCOLOR)
                self.draw_text(TITLE,48,WHITE,WIDTH/2,HEIGHT/4)
                self.draw_text("Arrows to move, Space to jump",22,WHITE,WIDTH/2,HEIGHT/2)
                self.draw_text("Press a key to play",22,WHITE,WIDTH/2,HEIGHT*3/4)
                self.draw_text("High Score:"+str(self.highscore),22,WHITE,WIDTH/2,HEIGHT*1/10)
                
                self.all_sprites = pg.sprite.LayeredUpdates()
                boy = Player(self)
                girl = Player(self,'ninja_girl')
                self.all_sprites.add(boy)
                self.all_sprites.add(girl)
                self.all_sprites.update()
                
                waiting = True
                while waiting:

                        mouse = pg.mouse.get_pos()
                        click = pg.mouse.get_pressed()
                        if click[0] == 1: waiting = False
                        
                        if boy.rect.right > mouse[0] > boy.rect.left \
                        and boy.rect.bottom > mouse[1] > boy.rect.top:
                                self.player_outlook = 'ninja_boy'
                        if girl.rect.right > mouse[0] > girl.rect.left \
                        and girl.rect.bottom > mouse[1] > girl.rect.top:
                                self.player_outlook = 'ninja_girl'
                                                                
                        if self.player_outlook == 'ninja_boy': boy.update() 
                        else: girl.update()
                        girl.rect.midbottom = (WIDTH/2+girl.rect.width/2,HEIGHT/2+1.5*girl.rect.height)
                        boy.rect.midbottom = (WIDTH/2-boy.rect.width/2,HEIGHT/2+1.5*girl.rect.height)

                        self.all_sprites.draw(self.screen)
                        pg.display.flip()
                        for event in pg.event.get():
                                if event.type == pg.QUIT:
                                        waiting = False
                                        self.running = False
                                if event.type == pg.KEYUP:
                                        waiting = False
                pg.mixer.music.fadeout(500)
                
        def show_go_screen(self):
                # game over/continue
                if not self.running:
                        return
                pg.mixer.music.load(path.join(self.snd_dir,'Depressed of Happytown.ogg'))
                pg.mixer.music.play(loops=-1)                        
                self.screen.fill(BGCOLOR)
                self.draw_text("GAME OVER",48,WHITE,WIDTH/2,HEIGHT/4)
                self.draw_text("Your score was:"+str(self.score),22,WHITE,WIDTH/2,HEIGHT/2)
                self.draw_text("Press a key to start again",22,WHITE,WIDTH/2,HEIGHT*3/4)
                
                if self.score > self.highscore:
                        self.highscore = self.score
                        self.draw_text("New High Score!",22,WHITE,WIDTH/2,HEIGHT/2-48)
                        with open(path.join(self.dir,HS_FILE),'w') as f:
                                f.write(str(self.score))
                pg.display.flip()
                self.wait_for_key()
                pg.mixer.music.fadeout(500)
                
        def wait_for_key(self):
                waiting = True
                while waiting:
                        self.clock.tick(FPS)
                        for event in pg.event.get():
                                if event.type == pg.QUIT:
                                        waiting = False
                                        self.running = False
                                if event.type == pg.KEYUP:
                                        waiting = False
                                        
                                self.music_volume_event(event)
                                
        def draw_text(self,text,size,color,x,y):
                font = pg.font.Font(self.font_name,size)
                text_surface = font.render(text,True,color)
                text_rect = text_surface.get_rect()
                text_rect.midtop = (x,y)
                self.screen.blit(text_surface,text_rect)
                
                
g = Game()
g.show_start_screen()
while g.running:
        g.new()
        g.show_go_screen()
        
pg.quit()

        
