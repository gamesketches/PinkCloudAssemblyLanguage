import pygame, sys, os, math
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

class equalizingNumber():
    def __init__(self,number):
        self.number = number

    def add(self,number):
        if number < 0:
            if number + self.number > 0:
                return 0
            else:
                return number + self.number
        elif number > 0:
            if number - self.number < 0:
                return 0
            else:
                return number - self.number
        else:
            return 0

    def increase(self,number):
        self.number += number

class spreadBeaverNode():
    def __init__(self, directions):
        self.directions = directions #Should be "NORTH" "EAST" "WEST" or "SOUTH
        self.drawSurface = pygame.Surface((10,10))
        self.locked = False
        if "NORTH" in self.directions:
            pygame.draw.line(self.drawSurface, (250,250,250), (5,5),(5,0))
        if "EAST" in self.directions:
            pygame.draw.line(self.drawSurface, (250,250,250), (5,5),(10,5))
        if "WEST" in self.directions:
            pygame.draw.line(self.drawSurface, (250,250,250), (5,5),(0,5))
        if "SOUTH" in self.directions:
            pygame.draw.line(self.drawSurface, (250,250,250), (5,5), (5,10))

    def hasDirection(self,direction):
        if direction in self.directions:
            return True
        else:
            return False

class spreadBeaverGrid():
    def __init__(self):
        self.grid = []
        for i in xrange(100):
            tempList = []
            for j in xrange(60):
                tempList.append(spreadBeaverNode([]))
            self.grid.append(tempList)
        for i in xrange(60):
            self.grid[50][i] = spreadBeaverNode(["NORTH","SOUTH"])
        self.pos = [50,50]
        self.goalPos = [50,10]
        self.grid[50][51].locked = True
        self.cursor = pygame.Surface((10,10))
        self.cursor = self.cursor.convert()
        self.cursor.fill((255, 102, 204))
        self.goal = pygame.Surface((10,10))
        self.goal = self.goal.convert()
        self.goal.fill((255,255,0))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            if self.grid[self.pos[0]][self.pos[1]].hasDirection("EAST"):
                if not self.grid[self.pos[0] + 1][self.pos[1]].locked:
                    self.pos[0] += 1
        elif keys[K_DOWN]:
            if self.grid[self.pos[0]][self.pos[1]].hasDirection("SOUTH"):
                if not self.grid[self.pos[0]][self.pos[1] + 1].locked:
                    self.pos[1] += 1
        elif keys[K_LEFT]:
            if self.grid[self.pos[0]][self.pos[1]].hasDirection("WEST"):
                if not self.grid[self.pos[0] - 1][self.pos[1]].locked:
                    self.pos[0] -= 1
        elif keys[K_UP]:
            if self.grid[self.pos[0]][self.pos[1]].hasDirection("NORTH"):
                if not self.grid[self.pos[0]][self.pos[1] - 1].locked:
                    self.pos[1] -= 1
                
    def draw(self,screen):
        lock = pygame.Surface((10,10))
        lock.convert()
        lock.fill((0,0,200))
        for i in range(len(self.grid)):
            for k in range(len(self.grid[i])):
                screen.blit(self.grid[i][k].drawSurface, (i * 10, k * 10))
                if self.grid[i][k].locked:
                    screen.blit(lock, (i * 10, k * 10))
        screen.blit(self.cursor, (self.pos[0] * 10, self.pos[1] * 10))
        screen.blit(self.goal, (self.goalPos[0] * 10, self.goalPos[1] * 10))

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
        self.sprite.rect.center = (500,300)
        self.offset = [0,0]
        self.trueWidth = self.sprite.rect.width
        self.trueHeight = self.sprite.rect.height

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            if self.slope['y'] > -6:
                self.slope['y'] -= 1
        elif keys[K_DOWN]:
            if self.slope['y'] < 6:
                self.slope['y'] += 1
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
        self.sprite.rect = self.sprite.rect.move(self.slope['x'],self.slope['y'])
        self.offset[0] += self.slope['x']
        self.offset[1] -= self.slope['y']
        self.trueWidth -= 0.01
        self.trueHeight -= 0.01
        self.sprite.rect.width = self.trueWidth
        self.sprite.rect.height = self.trueHeight
        self.sprite.image = pygame.transform.scale(self.sprite.image,(self.sprite.rect.width, self.sprite.rect.height))

    def eat(self):
        self.trueWidth += 10
        self.trueHeight += 10
        self.sprite.image = pygame.transform.scale(self.sprite.image,(self.sprite.rect.width, self.sprite.rect.height))

class doubtEnemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("fly.png", -1)
        self.rect.center = (randint(-1000,2000),randint(-600,1200))
        self.velocity = [0,0]
        self.acceleration = 0

    def update(self):
        if abs(self.velocity[0]) <= 0 and abs(self.velocity[1]) <= 0:
            self.acceleration = equalizingNumber(0.0003)
            self.velocity[randint(0,1)] = randint(-6,6)
        else:
            self.acceleration.number *= 2
            if abs(self.velocity[0]) > 0:
                self.velocity[0] = self.acceleration.add(self.velocity[0])
                if abs(self.velocity[0]) <= 0:
                    self.velocity[0] = 0
            if abs(self.velocity[1]) > 0:
                self.velocity[1] = self.acceleration.add(self.velocity[1])
                if abs(self.velocity[1]) <= 0:
                    self.velocity[1] = 0
            
            self.rect = self.rect.move((self.velocity[0],self.velocity[1]))

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

class everFreePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("breedingHide.png", -1)
        self.velocity = [False,True]
        self.slope = [0,5]
        self.touchingSurface = False
        self.unattachableTime = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            self.velocity[0] = True
        elif keys[K_LEFT]:
            self.velocity[0] = -1
        else:
            self.velocity[0] = False
        if keys[K_UP]:
            if self.touchingSurface:
                self.unattachableTime = 30
                if self.slope[0] == 0:
                    self.slope = [5,5]
                    # If attached to a vertial wall on the right side
                    if self.touchingSurface.position[0] > self.rect.centerx:
                        self.detachFromSurface([-1,-1])
                    else:
                        self.detachFromSurface([1,-1])
                else:
                    self.slope = [5,5]
                    self.detachFromSurface([False,-1])
        
        self.rect = self.rect.move(self.slope[0] * self.velocity[0], self.slope[1] * self.velocity[1])
        if self.touchingSurface and self.slope[0] != 0:
            self.rect.y = self.touchingSurface.returnHeight(self.rect.centerx) - self.rect.height

        if self.unattachableTime:
            self.unattachableTime -= 1
            self.velocity[1] = -1
        elif not self.touchingSurface:
            self.velocity[1] = 1

    def changeOrientation(self,slope):
        if slope[0] != 0:
            self.image = pygame.transform.rotate(self.image, math.degrees(math.atan(slope[1]/slope[0])) * -1)
        self.slope = slope

    def attachToSurface(self,surface):
        self.touchingSurface = surface
        if surface.slope[0] == 0:
            if surface.position[0] > self.rect.x:
                self.rect.x = surface.position[0] - self.rect.width + 1
            else:
                self.rect.x = surface.position[0] - 1
        else:
            self.rect.y = surface.returnHeight(self.rect.x) - self.rect.height
            self.rect.bottom = surface.returnHeight(self.rect.centerx)
        self.changeOrientation(surface.slope)
        self.velocity = surface.velocityProfile

    def detachFromSurface(self, velocityProfile):
        self.touchingSurface = False
        self.velocity = velocityProfile
        self.image, temp = load_image("breedingHide.png", -1)
        
class everFreeSurface():
    def __init__(self,slope,position,drag,length, velocityProfile):
        self.slope = slope
        self.position = position
        self.drag = drag
        self.velocityProfile = [False,False]
        self.length = length
        if slope[0] == 0:
            self.drawSurface = pygame.Surface((5,length))
        else:
            self.drawSurface = pygame.Surface((length, (length / slope[0]) * slope[1]))
        self.drawSurface = self.drawSurface.convert()
        self.drawSurface.fill((0,0,0))
        if slope[0] == 0:
            pygame.draw.line(self.drawSurface,(250,250,250), (0,0),(0,self.drawSurface.get_height()))
        else:
            pygame.draw.line(self.drawSurface,(250,250,250),(0,0),(self.length,self.drawSurface.get_height()))

    def draw(self,screen):
        screen.blit(self.drawSurface,self.position)

    def collideableRect(self):
        return self.drawSurface.get_rect().move(self.position)

    def returnHeight(self,x):
        x -= self.position[0]
        if self.slope[0] == 0:
            return x
        else:
            return (x * (float(self.slope[1]) / self.slope[0])) + self.position[1]
        
    
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
        self.image, self.rect = load_image('breedingHide.png',-1)
        self.carrying = False
        self.facingRight = True
        self.image = pygame.transform.flip(self.image, True, False)
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
                    self.image = pygame.transform.flip(self.image, True, False)
                else:
                    self.moveLeft()
                self.locked = True
            elif keys[K_RIGHT]:
                if self.facingRight:
                    self.moveRight()
                else:
                    self.facingRight = True
                    self.image = pygame.transform.flip(self.image, True, False)
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

class hurryGoRoundPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("breedingHide.png", -1)
        self.rect.x = 10
        self.rect.y = 500
        self.offset = 0

    def update(self):
        self.rect.x += 5

    def draw(self,screen):
        screen.blit(self.image, (10 + self.offset,self.rect.y))

class hurryGoRoundFootprint(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("magmaBall.png", -1)
        self.rect.midbottom = position

    def draw(self,screen, offset, x):
        screen.blit(self.image,(self.rect.x - x + offset, self.rect.y))

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
    # Change track to Rocket Dive
    if gameData['trackNumber'] == 1:
        gameData['player'] = rocketDivePlayer()
        gameData['spriteList'].add(gameData['player'])
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
        for i in range(6):
            gameData['spriteList'].add(doubtEnemy())
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        gameData['backGround'] = newBackground
    # Change track to Fish Scratch Fever    
    elif gameData['trackNumber'] == 5: 
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        pygame.draw.polygon(newBackground,(20,40,200),[(0,600),(470,340),(530,340),(1000,600)])
        gameData['backGround'] = newBackground
        gameData['player'] = fishScratchFeverPlayer()
        gameData['spriteList'].add(fishScratchFeverObstacle())
    # Change track to Ever Free
    elif gameData['trackNumber'] == 6:
        gameData['player'] = everFreePlayer()
        gameData['player'].rect.center = (500,200)
        gameData['surfaces'] = [everFreeSurface([10,3],(200,200),1,400, [True,False])]
        gameData['surfaces'].append(everFreeSurface([0,5],(800,200),1,400,[False,False]))
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        gameData['backGround'] = newBackground
    # Change track to Breeding
    elif gameData['trackNumber'] == 7:
        gameData['grid'] = breedingGrid()
        gameData['grid'].columns[0].height = 2
        gameData['grid'].columns[1].height = 1
        gameData['player'] = gameData['grid'].player
        gameData['spriteList'].add(gameData['player'])
        gameData['backGround'].fill((0,0,0))
    # Change track to Hurry Go Round
    elif gameData['trackNumber'] == 8:
        gameData['player'] = hurryGoRoundPlayer()
        gameData['spriteList'].add(gameData['player'])
        gameData['frameCounter'] = 20
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
    player1LifeMeter = Meter((800,0,200,60), (0,255,0),(200,200,200), 100, 100)
    meteors = pygame.sprite.Group(rocketDiveMeteor((300,600)))
    frameTimer = 30
    speed = 5
    trackNumber = 1
    allsprites = pygame.sprite.Group()
    gameData = {'player': None,'trackNumber':trackNumber,'spriteList':allsprites,'background':background,'distance':1000}
    distanceTracker = pygame.font.Font(None, 36)

    grid = spreadBeaverGrid()
    
    going = True
    while going:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
            elif event.type == KEYDOWN and event.key == K_p:
                allsprites.empty()
                changeTrack(gameData)

        screen.blit(background, (0,0))
        # ----- Track 1, Spread Beaver -----
        if gameData['trackNumber'] == 1:
            grid.update()
            grid.draw(screen)
            if grid.pos == grid.goalPos:
                changeTrack(gameData)
        # ----- Track 2, Rocket Dive -------
        elif gameData['trackNumber'] == 2:
            frameTimer -= 1

            speed += 0.005
            gameData['distance'] -= (speed / 50)
            
            if frameTimer == 0:
                meteors.add(rocketDiveMeteor((randint(0,1000),600)))
                frameTimer = 30 + randint(-3,20)
            for i in meteors.sprites():
                if gameData['player'].rect.colliderect(i.rect):
                    gameData['player'].life -= 50
                    player1LifeMeter.update(player1.life)
                    i.kill()
                    if gameData['player'].life == 0:
                        changeTrack(gameData)
                        meteors.empty()
                        break
            if gameData['distance'] <= 0:
                changeTrack(gameData)
                meteors.empty()
            meteors.update(speed)
            meteors.draw(screen)
            player1LifeMeter.draw(screen)
            screen.blit(distanceTracker.render(str(gameData['distance']), 1, (200,10,10)), (900,500))
        # ----- Track 3, Leather Face -------
        elif gameData['trackNumber'] == 3:
            for i in allsprites.sprites():
                if type(i) == leatherFaceTarget:
                    i.rect.x += -1 * gameData['player'].velocity
                    if i.rect.colliderect(gameData['player'].rect):
                        i.runAway()
                    if not i.facingRight and gameData['player'].visible:
                        changeTrack(gameData)
                        frameTimer = 50
        # ----- Track 4, Pink Spider -------
        elif gameData['trackNumber'] == 4:
            screen.blit(gameData['backGround'], (0,0))
            frameTimer -= 1
            if frameTimer == 0:
                allsprites.add(pinkSpiderFly())
                frameTimer = 200
            for i in allsprites.sprites():
                if type(i) != pinkSpiderPlayer and gameData['player'].rect.colliderect(i.rect):
                    i.getCaught()
                    changeTrack(gameData)
        # ----- Track 5, Doubt '97 -----
        elif gameData['trackNumber'] == 5:
            allsprites = pygame.sprite.Group()
            screen.blit(gameData['backGround'], (0,0))
            gameData['spriteList'].update()
            gameData['player'].update()
            offset = gameData['player'].offset
            screen.blit(gameData['player'].sprite.image, (500,300))
            for i in gameData['spriteList'].sprites():
                screen.blit(i.image, (i.rect.x - offset[0], i.rect.y + offset[1]))
                if i.rect.colliderect(gameData['player'].sprite.rect):
                    i.kill()
                    gameData['player'].eat()
            if gameData['player'].sprite.rect.width < 5:
                changeTrack(gameData)
        # ----- Track 6, Fish Scratch Fever -----
        elif gameData['trackNumber'] == 6:
            screen.blit(gameData['backGround'],(0,0))
            allsprites = gameData['spriteList']
            curSpeed = gameData['player'].update()
            gameData['player'].draw(screen)
            for i in allsprites.sprites():
                i.updateDistance(curSpeed)
                if i.distance <= 0:
                    if gameData['player'].gameOverKa(i.type):
                        changeTrack(gameData)
        # ----- Track 7, Ever Free -----
        elif gameData['trackNumber'] == 7:
            screen.blit(gameData['backGround'],(0,0))
            allsprites.add(gameData['player'])
            for i in gameData['surfaces']:
                i.draw(screen)
                if not gameData['player'].unattachableTime:                        
                    if i != gameData['player'].touchingSurface:
                        if gameData['player'].rect.colliderect(i.collideableRect()):
                            gameData['player'].attachToSurface(i)
                    else:
                        if not gameData['player'].rect.colliderect(i.collideableRect()):
                            gameData['player'].detachFromSurface([0,6])
        # ----- Track 8, Breeding ------
        elif gameData['trackNumber'] == 8:
            screen.blit(gameData['background'], (0,0))
            gameData['grid'].draw(screen)
        # ----- Track 9 Hurry Go Round -----
        elif gameData['trackNumber'] == 9:
            allsprites = pygame.sprite.Group()
            screen.blit(gameData['background'], (0,0))
            if gameData['frameCounter'] == 0:
                gameData['spriteList'].add(hurryGoRoundFootprint(gameData['player'].rect.bottomleft))
                #allsprites.add(hurryGoRoundFootprint(gameData['player'].rect.bottomleft))
                gameData['frameCounter'] = 20
            else:
                gameData['frameCounter'] -= 1
            gameData['player'].update()
            for i in gameData['spriteList'].sprites():
                if type(i) is hurryGoRoundPlayer:
                    i.draw(screen)
                else:
                    i.draw(screen,gameData['player'].offset,gameData['player'].rect.x)
            
            
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
