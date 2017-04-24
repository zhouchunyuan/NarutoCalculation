#sprites

import pygame as pg
from settings import *
from random import choice, randrange
from os import path
vec = pg.math.Vector2

class Spritesheet:
        # utility class for loading and parsing spritesheets
        def __init__(self, filename):
                self.spritesheet = pg.image.load(filename).convert()
        def get_image(self,x,y,width,height):
                #grab an image out of a larger spritesheet
                image = pg.Surface((width,height))
                image.blit(self.spritesheet,(0,0),(x,y,width,height))
                image = pg.transform.scale(image,(width//2,height//2))
                return image
                
class Player(pg.sprite.Sprite):
        def __init__(self,game,imgfolder = 'ninja_boy'):
                self._layer = PLAYER_LAYER
                self.groups =game.all_sprites
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                self.walking = False
                self.jumping = False
                self.lowdown = False
                self.ninja_dir = imgfolder
                self.dead = False
                self.scale_factot = 0.2
                self.current_frame = 0
                self.last_update = 0
                self.load_images()
                #self.image = pg.Surface((30,40))
                #self.image.fill(YELLOW)
                self.image = self.standing_frames[0]
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.center = (40,HEIGHT-100)
                self.pos = vec(40,HEIGHT-100)
                self.vel = vec(0,0)
                self.acc = vec(0,0)
                self.magic_on = False
                
        def load_images(self):
                self.standing_frames = [self.game.spritesheet.get_image(614,1063,120,192),
                                        self.game.spritesheet.get_image(690,406,120,201)]
                for frame in self.standing_frames:
                        frame.set_colorkey(BLACK)
                self.walk_frames_r = [self.game.spritesheet.get_image(678,868,120,201),
                                      self.game.spritesheet.get_image(692,1458,120,207)]
                for frame in self.walk_frames_r:
                        frame.set_colorkey(BLACK)                                      
                self.walk_frames_l = []
                for frame in self.walk_frames_r:
                        self.walk_frames_l.append(pg.transform.flip(frame,True,False))
                self.jump_frame = self.game.spritesheet.get_image(382,763,150,181)
                
                self.ninja = {}
                self.ninjaL= {}
                self.ninja['Idle'] =[]
                self.ninja['Run'] =[]
                self.ninja['Jump'] =[]
                self.ninja['Slide'] =[]
                self.ninja['Dead'] =[]
                self.ninjaL['Idle'] =[]
                self.ninjaL['Run'] =[]
                self.ninjaL['Jump'] =[]
                self.ninjaL['Slide'] =[]
                self.ninjaL['Dead'] =[]
                self_dir = path.dirname(__file__)
                img_dir = path.join(self_dir,'img')
                img_dir = path.join(img_dir,self.ninja_dir)
                for action in self.ninja.keys():
                        for i in range(10):
                                filename = action+'__00{}.png'.format(i)
                                img = pg.image.load(path.join(img_dir,filename)).convert()
                                img.set_colorkey(BLACK)
                                
                                img = pg.transform.scale(img,( int(img.get_rect().w*self.scale_factot),
                                                               int(img.get_rect().h*self.scale_factot)))
                                self.ninja[action].append(img)
                                self.ninjaL[action].append(pg.transform.flip(img,True,False))
        def jump_cut(self):
                if self.jumping:
                        if self.vel.y < -3:
                                self.vel.y = -3
        def jump(self):
                # jump only if standing on a platform
                self.rect.y += 2
                hits = pg.sprite.spritecollide(self,self.game.platforms, False)
                self.rect.y -= 2
                if hits and not self.jumping:
                        self.game.jump_sound.play()
                        self.jumping = True
                        self.vel.y = -PLAYER_JUMP
        def jump_to(self,x,y):
                self.pos = (x,y)
                
        def update(self):
                if not self.dead:
                        self.animate()
                        self.acc = vec(0,PLAYER_GRAV)
                        keys = pg.key.get_pressed()
                        if keys[pg.K_LEFT]:
                                self.acc.x = -PLAYER_ACC
                        if keys[pg.K_RIGHT]:
                                self.acc.x = PLAYER_ACC

                        # apply friction
                        self.acc.x += self.vel.x * PLAYER_FRICTION
                        # equations of motion
                        self.vel += self.acc
                        if abs(self.vel.x)<0.1:
                                self.vel.x = 0
                        self.pos += self.vel + 0.5*self.acc
                        # wrap around the sides of the screen
                        if self.pos.x > WIDTH+self.rect.width/2:
                                self.pos.x = 0
                        if self.pos.x < 0 - self.rect.width/2:
                                self.pos.x = WIDTH
                        
                        self.rect.midbottom = self.pos
        def animate(self):
                now = pg.time.get_ticks()
                if self.vel.x != 0:
                        self.walking = True
                else:
                        self.walking = False
                
                # show walk animation
                if self.walking :
                        if self.magic_on :
                                standing_frames = self.standing_frames
                                walk_frames_l = self.walk_frames_l
                                walk_frames_r = self.walk_frames_r
                      
                        else:
                                standing_frames = self.ninja['Idle']
                                if self.vel.x * self.acc.x < 0:
                                        walk_frames_l = self.ninjaL['Slide']
                                        walk_frames_r = self.ninja['Slide']
                                else:
                                        walk_frames_l = self.ninjaL['Run']
                                        walk_frames_r = self.ninja['Run']
                        if now - self.last_update > 50:
                                self.last_update = now
                                self.current_frame = (self.current_frame + 1) % len(standing_frames)
                                bottom = self.rect.bottom
                                if self.vel.x > 0:
                                        self.image = walk_frames_r[self.current_frame]
                                else:
                                        self.image = walk_frames_l[self.current_frame]
                                self.rect = self.image.get_rect()
                                self.rect.bottom = bottom
                # show idle animation
                if not self.jumping and not self.walking:
                        if self.magic_on:
                                standing_frames = self.standing_frames
                        else:
                                standing_frames = self.ninja['Idle']
                        if now - self.last_update > 50:
                                self.last_update = now
                                self.current_frame = (self.current_frame + 1) % len(standing_frames)
                                bottom = self.rect.bottom
                                self.image = standing_frames[self.current_frame]
                                if self.lowdown:
                                        self.image = pg.transform.scale(self.image,(50,60))
                                self.rect = self.image.get_rect()
                                self.rect.bottom = bottom
                self.mask = pg.mask.from_surface(self.image)
class Cloud(pg.sprite.Sprite):
        def __init__(self,game):
                self._layer = CLOUD_LAYER
                self.groups =game.all_sprites,game.clouds
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                self.image = choice(self.game.cloud_images)
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                scale = randrange(50,101)/100
                self.image = pg.transform.scale(self.image, (int(self.rect.width*scale),
                                                             int(self.rect.height*scale)))
                self.rect.x = randrange(WIDTH - self.rect.width)
                self.rect.y = randrange(-500,-50)
        def update(self):
                if self.rect.top > HEIGHT:
                        self.kill()
class Platform(pg.sprite.Sprite):
        def __init__(self,game,x,y):
                self._layer = PLATFORM_LAYER
                self.groups =game.all_sprites,game.platforms
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                images = [self.game.spritesheet.get_image(0,288,380,94),
                          self.game.spritesheet.get_image(213,1662,201,100),
                          self.game.spritesheet.get_image(0,672,380,94),
                          self.game.spritesheet.get_image(208,1879,201,100),
                          self.game.spritesheet.get_image(0,768,380,94),
                          self.game.spritesheet.get_image(218,1764,201,100)]
                self.image = choice(images)
                self.image.set_colorkey(BLACK)
                self.image_copy = self.image.copy()
                #self.image = pg.Surface((w,h))
                #self.image.fill(GREEN)
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
                self.had_player = False
                self.has_player = False
                
                self.numA = randrange(11,20)
                self.numB = randrange(11,20)
                
                # spawn boost powerups
                if randrange(100) < POW_SPAWN_PCT:
                        Pow(self.game,self)
        def update(self):
                hit = pg.sprite.collide_rect(self,self.game.player)
                self.has_player = hit and abs(self.game.player.rect.bottom - self.rect.top) < 2
                
                if self.has_player and (not self.had_player):
                        # just jumped on
                        self.image = self.image_copy.copy()
                        self.numA = randrange(CALC_MIN,CALC_MAX)
                        self.numB = randrange(CALC_MIN,CALC_MAX)
                        color = choice([RED,GREEN,BLUE,BLACK])
                        self.draw_text( '{} x {}'.format(str(self.numA),str(self.numB)),
                                        25,color)
                        #self.game.active_platform = self # let the game know I am active
                if (not self.has_player) and self.had_player:
                        # just jumped off
                        self.image = self.image_copy.copy()
                        #self.game.active_platform = None # cancel active
                        
                self.had_player = self.has_player
                
        def draw_text(self,text,size,color):
                font = pg.font.Font(self.game.font_name,size)
                text_surface = font.render(text,True,color)
                x2,y2 = self.image.get_rect().center
                x1,y1 = text_surface.get_rect().center
                x = x2-x1
                y = y2-y1
                w = text_surface.get_rect().width
                h = text_surface.get_rect().height
                if self.rect.centerx + w > WIDTH:
                        x = x - w/2 - 5
                if x < 0:
                        x = 0
                if self.rect.centery + h > HEIGHT:
                        y = y - h/2 -3
                self.image.blit(text_surface,(x,y))
        def check_whiteboard_answer(self):
                text = self.game.whiteboard.text
                try:
                        answer = int(text)
                except:
                        answer = 0
                
                if answer == self.numA*self.numB:
                        self.image = self.image_copy.copy()
                        self.draw_text('good job!',22,GREEN)
                        result = True
                else:
                        result = False#self.draw_text('sorry ...',22,BLACK)
                return result
class Whiteboard(pg.sprite.Sprite):
        def __init__(self,game):
                self._layer = WHITEBOARD_LAYER
                self.groups =game.all_sprites
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                self.image = pg.Surface((100,40))
                self.image.fill(WHITE)
                self.rect = self.image.get_rect()
                self.text = ''
               
        def draw_text(self,text,size,color):
                font = pg.font.Font(self.game.font_name,size)
                text_surface = font.render(text,True,color)
                x2,y2 = self.image.get_rect().center
                x1,y1 = text_surface.get_rect().center
                x = x2-x1
                y = y2-y1
                self.image.blit(text_surface,(x,y)) 
        def update(self):
                self.rect.x = self.game.player.rect.x
                self.rect.y = self.game.player.rect.top - 2
                self.image.fill(WHITE)
                self.draw_text(self.text,22,RED)
class Pow(pg.sprite.Sprite):
        def __init__(self,game,plat):
                self._layer = POW_LAYER
                self.groups =game.all_sprites,game.powerups
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                self.plat = plat
                self.type = choice(['boost'])
                self.image = self.game.spritesheet.get_image(820,1805,71,70)
                self.image.set_colorkey(BLACK)
                self.mask = pg.mask.from_surface(self.image)
                self.rect = self.image.get_rect()
                self.rect.centerx = self.plat.rect.centerx
                self.rect.bottom = self.plat.rect.top-5
        def update(self):
                self.rect.bottom = self.plat.rect.top-5
                if not self.game.platforms.has(self.plat):
                        self.kill()

class Mob(pg.sprite.Sprite):
        def __init__(self,game):
                self._layer = MOB_LAYER
                self.groups =game.all_sprites,game.mobs
                pg.sprite.Sprite.__init__(self,self.groups)
                self.game = game
                self.image_up = self.game.spritesheet.get_image(566,510,122,139)
                self.image_up.set_colorkey(BLACK)
                self.image_down = self.game.spritesheet.get_image(568,1530,122,135)
                self.image_down.set_colorkey(BLACK)
                self.image = self.image_up
                self.rect = self.image.get_rect()
                self.rect.centerx = choice([-100,WIDTH+100])
                self.vx = randrange(1,4)
                if self.rect.centerx > WIDTH:
                        self.vx *= -1
                self.rect.y = randrange(HEIGHT/2)
                self.vy = 0
                self.dy = 0.5

        def update(self):
                self.rect.x += self.vx
                self.vy += self.dy
                if self.vy > 3 or self.vy < -3:
                        self.dy *= -1
                center = self.rect.center
                if self.dy < 0 :
                        self.image = self.image_up
                else:
                        self.image = self.image_down
                self.rect = self.image.get_rect()
                self.rect.center = center
                self.rect.y += self.vy
                if self.rect.left > WIDTH+100 or self.rect.right < -100:
                        self.kill()

