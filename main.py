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
            self.velocity[1] = -3
        elif keys[K_DOWN]:
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
        

class doubtPlayer():
    def __init__(self):
        self.tail = []
        self.slope = {'x':0,'y':0}
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image, self.sprite.rect = load_image('hideRocketDive.png')

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            if self.slope['y'] < 6:
                self.slope['y'] += 1
        elif keys[K_DOWN]:
            if self.slope['y'] > -6:
                self.slope['y'] -= 1
        else:
            if self.slope['y'] < 0:
                self.slope['y'] += 0.3
            elif self.slope['y'] > 0:
                self.slope['y'] -= 0.3
        if keys[K_RIGHT]:
            if self.slope['x'] < 6:
                self.slope['x'] += 1
        elif keys[K_LEFT]:
            if self.slope['x'] > -6:
                self.slope['x'] -= 1
        else:
            if self.slope['x'] < 0:
                self.slope['x'] += 0.3
            elif self.slope['x'] > 0:
                self.slope['x'] -= 0.3
            

class fishScratchFeverPlayer():
    def __init__(self):
        self.fishNum = 4
        self.speed = 1
        self.state = "neutral"
        self.frameTimer = 0
        self.fishPic, temp = load_image("salmon.png", -1)
        self.fishShadow = pygame.Surface((30,30))
        self.fishShadow = self.fishShadow.convert()
        self.fishShadow.fill((20,40,200))
        pygame.draw.circle(self.fishShadow,(10,20,100),(15,15) ,15)

    def update(self):
        if self.state == "neutral":
            keys = pygame.key.get_pressed()
            if keys[K_UP]:
                self.state = "jumping"
                self.frameTimer = 80
            if keys[K_DOWN]:
                self.state = "submerged"
                self.frameTimer = 80
            self.speed += 0.01
        elif self.state is "jumping" or self.state == "submerged":
            self.frameTimer -= 1
            if self.frameTimer == 0:
                self.state = "neutral"
        return self.speed

    def draw(self, screen):
        if self.state is "neutral":
            screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic, True, False), - 25),(250, 500))
            screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic,True,False), -12), (380,520))
            screen.blit(pygame.transform.rotate(self.fishPic, 12), (620,520))
            screen.blit(pygame.transform.rotate(self.fishPic, 25), (750, 500))
        elif self.state is "jumping":
            screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic, True, False), - 25),(250, 400))
            screen.blit(self.fishShadow, (250,500))
            screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic,True,False), -12), (380,420))
            screen.blit(self.fishShadow, (380, 520))
            screen.blit(pygame.transform.rotate(self.fishPic, 12), (620,420))
            screen.blit(self.fishShadow, (620, 520))
            screen.blit(pygame.transform.rotate(self.fishPic, 25), (750, 400))
            screen.blit(self.fishShadow, (750, 500))
        elif self.state is "submerged":
            screen.blit(self.fishShadow, (250,500))
            screen.blit(self.fishShadow, (380, 520))
            screen.blit(self.fishShadow, (620, 520))
            screen.blit(self.fishShadow, (750, 500))

    def gameOverKa(self, obstacle):
        print "gameOverKa with argument: ", obstacle
        if obstacle is "log":
            if self.state is "jumping":
                return False
            else:
                return True
        
class fishScratchFeverObstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        typeList = {0:"log",1:"bear",2:"food",3:"Damn"}
        self.type = typeList[randint(0,3)]
        self.distance = 100
        if self.type == "log":
            self.image, self.rect = load_image("log.png", -1)
        else:
            self.image, self.rect = load_image("log.png", -1)
            self.type = "log"
        self.originalImage = self.image
        self.rect.topleft = (470, 340)

    def updateDistance(self, speed):
        self.distance -= speed
        self.rect.y += 2 * speed
        if self.distance <= 0:
            self.kill()
        
    def update(self):
        scaleWidth = self.originalImage.get_width() - int(self.distance)
        scaleHeight = self.originalImage.get_height() - (int(self.distance) / 2)
        if scaleWidth < 0:
            scaleWidth = 1
        if scaleHeight < 0:
            scaleHeight = 1
        self.image = pygame.transform.scale(self.originalImage, (scaleWidth, scaleHeight))
        self.rect.centerx = 500

class breedingGrid():
    def __init__(self):
        self.player = breedingPlayer(self)
        self.goal = pygame.sprite.Sprite()
        self.goal.image, self.goal.rect = load_image("magmaBall.png")
        self.goal.rect.topleft = (900,50)
        self.columns = []
        self.NUMCOLUMNS = 10
        for i in range(self.NUMCOLUMNS):
            self.columns.append(breedingColumn(i))

    def draw(self,screen):
        for i in range(self.NUMCOLUMNS):
            self.columns[i].drawColumn(screen)
        if self.player.carrying:
            pygame.draw.rect(screen,(250,0,0),pygame.Rect(self.player.rect.left,self.player.rect.top - 100, 100, 100))
        screen.blit(self.goal.image, self.goal.rect.topleft)

    def allowMove(self,position, goingRight):
        if goingRight:
            if position < 9:
                if abs(self.columns[position].height - self.columns[position + 1].height) <= 1:
                    self.player.rect.bottom = 600 - self.columns[position +1].height * 100
                    return True
                else:
                    return False
            else:
                return False
        else:
            if position > 0:
                if abs(self.columns[position].height - self.columns[position -1].height) <= 1:
                    self.player.rect.bottom = 600 - self.columns[position -1].height * 100
                    return True
                else:
                    return False
            else:
                return False

    def allowAction(self, position, facingRight, action):
        if facingRight and position < 9:
            if abs(self.columns[position].height - self.columns[position +1].height) <= 1:
                if action is "pickup" and self.columns[position +1].height > 0:
                    self.columns[position + 1].removeBlock()
                    return True
                elif action is "drop":
                    self.columns[position + 1].addBlock()
                    return True
                else:
                    return False
            else:
                return False
        elif position > 0:
            if abs(self.columns[position].height - self.columns[position -1].height) <= 1:
                if action is "pickup" and self.columns[position -1].height > 0:
                    self.columns[position -1].removeBlock()
                    return True
                elif action is "drop":
                    self.columns[position -1].addBlock()
                    return True
                else:
                    return False
            else:
                return False

class breedingColumn():
    def __init__(self, number):
        self.height = 0
        self.occupied = False
        self.number = number

    def addBlock(self):
        self.height += 1
        
    def removeBlock(self):
        if self.height > 0:
            self.height -= 1
        
    def drawColumn(self,screen):
        for i in range(self.height + 1):
            pygame.draw.rect(screen, (250,0,0), pygame.Rect((self.number + 1) * 100,600-i*100, 100, 100))

class breedingPlayer(pygame.sprite.Sprite):
    def __init__(self, grid):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideRocketDive.png',-1)
        self.carrying = False
        self.facingRight = True
        self.locked = False
        self.grid = grid
        self.position = 2
        self.rect.x = (self.position + 1) * 100
        self.rect.y = 600 - self.rect.height

    def update(self):
        keys = pygame.key.get_pressed()
        if self.locked is False:
            if keys[K_LEFT]:
                if self.facingRight:
                    self.facingRight = False
                else:
                    self.moveLeft()
                self.locked = True
            elif keys[K_RIGHT]:
                if self.facingRight:
                    self.moveRight()
                else:
                    self.facingRight = True
                self.locked = True
            elif keys[K_UP]:
                if not self.carrying:
                    if self.grid.allowAction(self.position, self.facingRight, "pickup"):
                        self.carrying = True
                self.locked = True
            elif keys[K_DOWN]:
                if self.carrying:
                    if self.grid.allowAction(self.position, self.facingRight, "drop"):
                        self.carrying = False
                self.locked = True
        else:
            if not keys[K_LEFT] and not keys[K_DOWN] and not keys[K_UP] and not keys[K_RIGHT]:
                self.locked = False
                

    def moveRight(self):
        if self.grid.allowMove(self.position, self.facingRight):
            self.position += 1
            self.rect.x += 100

    def moveLeft(self):
        if self.grid.allowMove(self.position, self.facingRight):
            self.position -= 1
            self.rect.x -= 100

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

def changeTrack(gameData):
    gameData['spriteList'].empty()
    # Change track to Leather Face
    if gameData['trackNumber'] == 2:
        gameData['player'] = leatherFacePlayer()
        gameData['spriteList'].add(gameData['player'],leatherFaceTarget())
    # Change track to Pink Spider
    elif gameData['trackNumber'] == 3:
        gameData['player'] = pinkSpiderPlayer()
        gameData['spriteList'].add(gameData['player'])
        gameData['backGround'], temp = load_image('spiderweb.png')
    # Change track to Doubt '97
    elif gameData['trackNumber'] == 4:
        gameData['player'] = doubtPlayer()
        gameData['spriteList'].add(gameData['player'].sprite)
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        gameData['backGround'] = newBackground
    # Change track to Fish Scratch Fever    
    elif gameData['trackNumber'] == 5: # remove this line later
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        pygame.draw.polygon(newBackground,(20,40,200),[(0,600),(470,340),(530,340),(1000,600)])
        gameData['backGround'] = newBackground
        gameData['player'] = fishScratchFeverPlayer()
        gameData['spriteList'].add(fishScratchFeverObstacle())
    # Change track to Breeding
    elif gameData['trackNumber'] == 6:
        gameData['grid'] = breedingGrid()
        gameData['grid'].columns[0].height = 2
        gameData['grid'].columns[1].height = 1
        gameData['player'] = gameData['grid'].player
        gameData['spriteList'].add(gameData['player'])
        gameData['backGround'].fill((0,0,0))
        gameData['trackNumber'] = 7 #remove this line later
    gameData['trackNumber'] += 1

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
    gameData = {'player': player1,'trackNumber':trackNumber,'spriteList':allsprites,'background':background}
    
    going = True
    while going:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_p:
                changeTrack(gameData)

        screen.blit(background, (0,0))
        # ----- Track 2, Rocket Dive -------
        if gameData['trackNumber'] == 2:
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
                        changeTrack(gameData)
                        meteors.empty()
                        break
            meteors.update(speed)
            meteors.draw(screen)
            player1LifeMeter.draw(screen)
        # ----- Track 3, Leather Face -------
        if gameData['trackNumber'] == 3:
            for i in allsprites.sprites():
                if type(i) == leatherFaceTarget:
                    i.rect.x += -1 * gameData['player'].velocity
                    if i.rect.colliderect(gameData['player'].rect):
                        i.runAway()
                    if not i.facingRight and gameData['player'].visible:
                        changeTrack(gameData)
                        frameTimer = 50
        # ----- Track 4, Pink Spider -------
        if gameData['trackNumber'] == 4:
            screen.blit(gameData['backGround'], (0,0))
            frameTimer -= 1
            if frameTimer == 0:
                allsprites.add(pinkSpiderFly())
                frameTimer = 200
            for i in allsprites.sprites():
                if type(i) != pinkSpiderPlayer and gameData['player'].rect.colliderect(i.rect):
                    i.getCaught()
                    changeTrack(gameData)
        # ----- Track 5, Doubt -----
        if gameData['trackNumber'] == 5:
            screen.blit(gameData['backGround'], (0,0))
            allsprites = gameData['spriteList']
        # ----- Track 6, Fish Scratch Fever -----
        if gameData['trackNumber'] == 6:
            screen.blit(gameData['backGround'],(0,0))
            allsprites = gameData['spriteList']
            curSpeed = gameData['player'].update()
            gameData['player'].draw(screen)
            for i in allsprites.sprites():
                i.updateDistance(curSpeed)
                if i.distance <= 0:
                    if gameData['player'].gameOverKa(i.type):
                        changeTrack(gameData)
        # ----- Track 8, Breeding ------
        if gameData['trackNumber'] == 8:
            screen.blit(gameData['background'], (0,0))
            gameData['grid'].draw(screen)
            
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
