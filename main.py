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

class rocketDivePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideRocketDive.png', -1)
        self.velocity = [0,0]

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
        self.image, self.rect = load_image('magmaBall.png')
        self.rect.x = loc[0]
        self.rect.y = loc[1]

    def update(self):
        self.rect.y -= 5

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
    meteor = rocketDiveMeteor((300,600))
    meteors = pygame.sprite.Group(meteor)
    allsprites = pygame.sprite.Group(player1, meteor)
    meteorTimer = 30

    going = True
    while going:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()

        screen.blit(background, (0,0))
        meteorTimer -= 1
        if meteorTimer == 0:
            meteors.add(rocketDiveMeteor((randint(0,1000),600)))
            meteorTimer = 30 + randint(-3,20)
        for i in meteors.sprites():
            if player1.rect.colliderect(i.rect):
                player1LifeMeter.update(50)
        player1LifeMeter.draw(screen)
        allsprites.update()
        allsprites.draw(screen)
        meteors.update()
        meteors.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
