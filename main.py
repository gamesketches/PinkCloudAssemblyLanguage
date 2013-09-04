import pygame, sys, os
from pygame.locals import *
from random import randint

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

main_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound

class leatherFacePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideLeatherFace.png', -1)
        self.velocity = 0
        self.rect.y = 400
        self.rect.x = 100
        self.visible = True

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.velocity = -3
        elif keys[K_RIGHT]:
            self.velocity = 3
        else:
            self.velocity = 0
        if keys[K_DOWN]:
            self.visible = False
        else:
            self.visible = True
        self.rect.x += self.velocity

class leatherFaceTarget(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('leatherfaceTarget.png', -1)
        self.velocity = 0
        self.rect.y = 400
        self.rect.x = 900
        self.facingRight = True
        self.switchTimer = 0
        self.state = "standing"

    def update(self):
        if self.state is "standing":                
            if self.facingRight:
                self.switchTimer += 1
                if self.switchTimer == 60:
                    self.facingRight = False
                    self.switchTimer = 0
                    self.image = pygame.transform.flip(self.image, True, False)
            else:
                self.switchTimer += 1
                if self.switchTimer == 10:
                    self.facingRight = True
                    self.switchTimer = 0
                    self.image = pygame.transform.flip(self.image, True, False)
        elif self.state is "running":
            self.frameTimer -= 1
            if self.frameTimer == 0:
                self.state = "standing"
            else:
                self.rect.x += 5

    def runAway(self):
        self.state = "running"
        self.frameTimer = 50
        self.facingRight = True

class pinkSpiderPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideRocketDive.png')
        self.velocity = [0,0]
        self.rect.x = 100
        self.rect.y = 500
        self.state = "grounded"

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.velocity[0] = -3
        elif keys[K_RIGHT]:
            self.velocity[0] = 3
        elif keys[K_UP]:
            #if self.state == "ladder" or self.rect.colliderect(ladderRect):
            #    self.state = "ladder"
            #    self.velocity[1] = 5
            self.velocity[1] = -3
        elif keys[K_DOWN]:
            #if self.state == "ladder":
            #    self.velocity[1] = -5
            self.velocity[1] = 3
        else:
            self.velocity[0] = 0
            self.velocity[1] = 0
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

class pinkSpiderFly(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('fly.png', -1)
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        self.rect.x = randint(0,1000)
        self.rect.y = randint(0,600)
        self.velocity = [5,0]
        self.caught = False
        self.frameTimer = 0
        self.wiggleTime = randint(3,6)

    def update(self):
        self.frameTimer += 1
        if self.frameTimer == self.wiggleTime:
            self.frameTimer = 0
            self.rect.x += self.velocity[0]
            self.velocity[0] *= -1

    def getCaught(self):
        self.caught = True
        self.image, temp = load_image('wrappedFly.png', -1)
        self.wiggleTime = 10
        

class pinkSpiderLadder(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('ladder.png')

class rocketDivePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideRocketDive.png', -1)
        self.velocity = [0,0]
        self.life = 100

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.velocity[0] = -3
        elif keys[K_RIGHT]:
            self.velocity[0] = 3
        else:
            self.velocity[0] = 0
        if keys[K_DOWN]:
            self.velocity[1] = 3
        elif keys[K_UP]:
            self.velocity[1] = -3
        else:
            self.velocity[1] = 0
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

class rocketDiveMeteor(pygame.sprite.Sprite):
    def __init__(self, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('asteroid.png')
        self.rect.x = loc[0]
        self.rect.y = loc[1]
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() + randint(-100, 100), self.image.get_height() + randint(-100,100)))

    def update(self,speed):
        self.rect.y -= speed
        if self.rect.bottom < 0:
            self.kill()

class Meter():
    def __init__(self,dimensions,barColor,frameColor,startingAmount, maxAmount):
        self.frame = pygame.Surface((dimensions[2],dimensions[3]))
        self.frame.fill(frameColor)
        self.barHeight = dimensions[3] *0.8
        self.barColor = barColor
        self.bar = pygame.Surface((dimensions[2] * 0.95, self.barHeight))
        self.bar.fill(barColor)
        self.perPixel = self.bar.get_width() / (maxAmount + 0.0)
        self.update(startingAmount)
        self.x = dimensions[0]
        self.y = dimensions[1]

    def update(self,amount):
        if amount > 0:
            self.bar = pygame.Surface((self.perPixel * amount, self.barHeight))
        else:
            self.bar = pygame.Surface((0,0))
        self.bar.fill(self.barColor)

    def draw(self,screen):
        screen.blit(self.frame, (self.x, self.y))
        screen.blit(self.bar, (self.frame.get_width() * 0.025 + self.x, self.frame.get_height() * 0.1))

def main():
    
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption('Pink Cloud Assembly Language')
    pygame.mouse.set_visible(0)

    #Create the background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0,0,0))

    #Display The Background
    screen.blit(background, (0,0))
    pygame.display.flip()

    #Prepare Game Objects
    clock = pygame.time.Clock()
    player1 = rocketDivePlayer()
    player1LifeMeter = Meter((800,0,200,60), (0,255,0),(200,200,200), 100, 100)
    meteors = pygame.sprite.Group(rocketDiveMeteor((300,600)))
    allsprites = pygame.sprite.Group(player1)
    frameTimer = 30
    speed = 5
    trackNumber = 2

    going = True
    while going:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()

        screen.blit(background, (0,0))
        # ----- Track 2, Rocket Dive -------
        if trackNumber == 2:
            frameTimer -= 1

            speed += 0.005
            if frameTimer == 0:
                meteors.add(rocketDiveMeteor((randint(0,1000),600)))
                frameTimer = 30 + randint(-3,20)
            for i in meteors.sprites():
                if player1.rect.colliderect(i.rect):
                    player1.life -= 50
                    player1LifeMeter.update(player1.life)
                    i.kill()
                    if player1.life == 0:
                        #transition to track 3
                        trackNumber = 3
                        allsprites.empty()
                        player1 = leatherFacePlayer()
                        allsprites.add(player1,leatherFaceTarget())
                        meteors.empty()
                        break
            meteors.update(speed)
            meteors.draw(screen)
            player1LifeMeter.draw(screen)
        # ----- Track 3, Leather Face -------
        if trackNumber == 3:
            for i in allsprites.sprites():
                if type(i) == leatherFaceTarget:
                    i.rect.x += -1 * player1.velocity
                    if i.rect.colliderect(player1.rect):
                        i.runAway()
                    if not i.facingRight and player1.visible:
                        player1.kill()
                        allsprites.empty()
                        player1 = pinkSpiderPlayer()
                        allsprites.add(player1)
                        trackNumber = 4
                        frameTimer = 50
                        spiderWebImage, temp = load_image("spiderweb.png")
        # ----- Track 4, Pink Spider -------
        if trackNumber == 4:
            screen.blit(spiderWebImage, (0,0))
            frameTimer -= 1
            if frameTimer == 0:
                allsprites.add(pinkSpiderFly())
                frameTimer = 200
                for i in allsprites.sprites():
                    if type(i) != pinkSpiderPlayer and player1.rect.colliderect(i.rect):
                        i.getCaught()
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
