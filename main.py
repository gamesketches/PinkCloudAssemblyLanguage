import pygame, sys, os, math
from pygame.locals import *
from random import randint
from interpolator import *

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
    def __init__(self, directions, lock, color):
        self.directions = directions #Should be "NORTH" "EAST" "WEST" or "SOUTH
        self.drawSurface = pygame.Surface((20,20))
        if color is "RED":
            self.color = (250,0,0)
            print "a red surface"
        elif color is "GREEN":
            self.color = (0,250,0)
        elif color is "BLUE":
            self.color = (0,0,250)
        elif color is "PINK":
            self.color = (255,102,204)
        elif color is "YELLOW":
            self.color = (255,255,0)
        else:
            self.color = (255,255,255)
        if lock is False:
            self.locked = False
            self.drawLines()
        elif lock is "UNLOCK":
            self.locked = "UNLOCK"
            self.drawSurface.fill(self.color)
        else:
            self.locked = True
            self.drawSurface.fill(self.color)
            
    def hasDirection(self,direction):
        if direction in self.directions:
            return True
        else:
            return False

    def drawLines(self):
        if "NORTH" in self.directions:
            pygame.draw.line(self.drawSurface, self.color, (5,5),(5,0))
        if "EAST" in self.directions:
            pygame.draw.line(self.drawSurface, self.color, (5,5),(10,5))
        if "WEST" in self.directions:
            pygame.draw.line(self.drawSurface, self.color, (5,5),(0,5))
        if "SOUTH" in self.directions:
            pygame.draw.line(self.drawSurface, self.color, (5,5), (5,10))

    def unlock(self,color):
        if self.color == color:
            if self.locked and self.locked is not "UNLOCK":
                self.locked = False
                self.drawSurface.fill((0,0,0))
                self.color = (255,255,255)
                self.drawLines()
            else:
                self.locked = True
                self.color = (0,0,0)
                self.drawSurface.fill(self.color)

class spreadBeaverGrid():
    def __init__(self):
        self.grid = []
        for i in xrange(50):
            tempList = []
            for j in xrange(30):
                tempList.append(spreadBeaverNode([],False,"WHITE"))
            self.grid.append(tempList)
        for i in xrange(30):
            self.grid[25][i] = spreadBeaverNode(["NORTH","SOUTH"], False, "WHITE")
        self.pos = [25,20]
        self.goalPos = [25,5]
        self.grid[25][26] = spreadBeaverNode(["NORTH","SOUTH"],True,"BLUE")
        self.cursor = pygame.Surface((20,20))
        self.cursor = self.cursor.convert()
        self.cursor.fill((255, 102, 204))
        self.goal = pygame.Surface((20,20))
        self.goal = self.goal.convert()
        self.goal.fill((255,255,0))
        self.cursorMovement = [None,0]

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            if self.cursorMovement[0] == "EAST":
                if self.cursorMovement[1] >= 3:
                    if self.grid[self.pos[0]][self.pos[1]].hasDirection("EAST"):
                        if self.grid[self.pos[0] +1][self.pos[1]].locked == "UNLOCK" or not self.grid[self.pos[0] + 1][self.pos[1]].locked:
                            self.pos[0] += 1
                    self.cursorMovement[1] = 0
                else:
                    self.cursorMovement[1] += 1
            else:
                self.cursorMovement[0] = "EAST"
                self.cursorMovement[1] = 0
        elif keys[K_DOWN]:
            if self.cursorMovement[0] == "SOUTH":
                if self.cursorMovement[1] >= 3:                            
                    if self.grid[self.pos[0]][self.pos[1]].hasDirection("SOUTH"):
                        if self.grid[self.pos[0]][self.pos[1]+1].locked == "UNLOCK" or not self.grid[self.pos[0]][self.pos[1] + 1].locked:
                            self.pos[1] += 1
                    self.cursorMovement[1] = 0
                else:
                    self.cursorMovement[1] += 1
            else:
                self.cursorMovement[0] = "SOUTH"
                self.cursorMovement[1] = 0
        elif keys[K_LEFT]:
            if self.cursorMovement[0] == "WEST":
                if self.cursorMovement[1] >= 3:                            
                    if self.grid[self.pos[0]][self.pos[1]].hasDirection("WEST"):
                        if self.grid[self.pos[0] - 1][self.pos[1]].locked == "UNLOCK" or not self.grid[self.pos[0] - 1][self.pos[1]].locked:
                            self.pos[0] -= 1
                    self.cursorMovement[1] = 0
                else:
                    self.cursorMovement[1] += 1
            else:
                self.cursorMovement[0] = "WEST"
                self.cursorMovement[1] = 0
        elif keys[K_UP]:
            if self.cursorMovement[0] == "NORTH":
                if self.cursorMovement[1] >= 3:                            
                    if self.grid[self.pos[0]][self.pos[1]].hasDirection("NORTH"):
                        if self.grid[self.pos[0]][self.pos[1] - 1].locked == "UNLOCK" or not self.grid[self.pos[0]][self.pos[1] - 1].locked:
                            self.pos[1] -= 1
                    self.cursorMovement[1] = 0
                else:
                    self.cursorMovement[1] += 1
            else:
                self.cursorMovement[0] = "NORTH"
                self.cursorMovement[1] = 0
                    
        if self.grid[self.pos[0]][self.pos[1]].locked == "UNLOCK":
            self.unlockGrid(self.grid[self.pos[0]][self.pos[1]].color)
            
        if self.pos == [25,5]:
            self.clearGrid()
            self.horizontalGridLine([0,15],[50,15],"WHITE")
            self.verticalGridLine([15,8],[15,15],"WHITE")
            self.horizontalGridLine([15,8],[40,8],"WHITE")
            self.grid[15][15] = spreadBeaverNode(["NORTH","WEST","EAST"], False, "WHITE")
            self.grid[15][8] = spreadBeaverNode(["EAST","SOUTH"],False,"WHTIE")
            self.grid[40][15] = spreadBeaverNode(["WEST","EAST"],True,"BLUE")
            self.grid[39][8] = spreadBeaverNode(["WEST"],"UNLOCK","BLUE")
            self.pos = [2,15]
            self.goalPos = [45,15]
            print "Passed level 1"
            
        elif self.pos == [45,15]:
            self.clearGrid()
            self.verticalGridLine([48,30],[48,20],"WHITE")
            self.horizontalGridLine([0,20],[48,20],"WHITE")
            self.grid[48][20] = spreadBeaverNode(["SOUTH","WEST"],False,"WHITE")
            self.grid[15][20] = spreadBeaverNode(["EAST","WEST"],True,"BLUE")
            self.verticalGridLine([40,20],[40,10],"WHITE")
            self.grid[40][20] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.verticalGridLine([30,20],[30,25],"WHITE")
            self.grid[30][20] = spreadBeaverNode(["EAST","WEST","SOUTH"],False,"WHITE")
            self.horizontalGridLine([20,10],[40,10],"WHITE")
            self.grid[40][10] = spreadBeaverNode(["SOUTH","WEST"],False,"WHITE")
            self.grid[20][10] = spreadBeaverNode(["EAST"],"UNLOCK","BLUE")
            self.grid[25][10] = spreadBeaverNode(["EAST","WEST"],True,"RED")
            self.horizontalGridLine([10,25],[30,25],"WHITE")
            self.grid[30][25] = spreadBeaverNode(["WEST","NORTH"],False,"WHITE")
            self.grid[10][25] = spreadBeaverNode(["EAST"],"UNLOCK","RED")
            self.pos = [48,28]
            self.goalPos = [5,20]
            print "Passed level 2"

        elif self.pos == [5,20]:
            self.clearGrid()
            self.horizontalGridLine([24,26],[50,26],"WHITE")
            self.verticalGridLine([24,0],[24,26],"WHITE")
            self.grid[24][26] = spreadBeaverNode(["EAST","NORTH"],False,"WHITE")
            self.horizontalGridLine([6,20],[24,20],"WHITE")
            self.grid[6][20] = spreadBeaverNode(["EAST"],"UNLOCK","PINK")
            self.grid[24][20] = spreadBeaverNode(["WEST","NORTH","SOUTH"],False,"WHITE")
            self.horizontalGridLine([24,15],[40,15],"WHITE")
            self.grid[24][15] = spreadBeaverNode(["EAST","NORTH","SOUTH"],False,"WHTIE")
            self.grid[40][15] = spreadBeaverNode(["WEST"],"UNLOCK","GREEN")
            self.horizontalGridLine([24,10],[4,10],"WHITE")
            self.grid[24][10] = spreadBeaverNode(["WEST","SOUTH","NORTH"],False,"WHITE")
            self.grid[4][10] = spreadBeaverNode(["EAST"],"UNLOCK","BLUE")
            self.grid[20][10] = spreadBeaverNode(["EAST","WEST"],False,"PINK")
            self.grid[24][5] = spreadBeaverNode(["NORTH","SOUTH"],True,"GREEN")
            self.grid[24][7] = spreadBeaverNode(["NORTH","SOUTH"],True,"PINK")
            self.grid[24][8] = spreadBeaverNode(["NORTH","SOUTH"],True,"BLUE")
            self.pos = [48,26]
            self.goalPos = [24,2]
            print "passed level 3"

        elif self.pos == [24,2]:
            self.clearGrid()
            self.horizontalGridLine([0,25],[50,25],"WHITE")
            self.verticalGridLine([10,25],[10,17],"WHITE")
            self.horizontalGridLine([10,17],[15,17],"WHITE")
            self.verticalGridLine([15,25],[15,17],"WHITE")
            self.grid[10][17] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.grid[10][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.grid[15][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.verticalGridLine([15,16],[15,7],"PINK")
            self.grid[15][7] = spreadBeaverNode(["SOUTH"],"UNLOCK","RED")
            self.horizontalGridLine([15,17],[20,17],"RED")
            self.grid[15][17] = spreadBeaverNode(["EAST","WEST","NORTH","SOUTH"],False,"WHITE")
            self.grid[16][17] = spreadBeaverNode(["EAST","WEST"],False,"RED")
            self.grid[15][16] = spreadBeaverNode(["SOUTH","NORTH"],False,"PINK")
            self.grid[20][17] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","BLUE")
            self.horizontalGridLine([21,17],[30,17],"BLUE")
            self.grid[21][17] = spreadBeaverNode(["EAST","WEST"],False,"BLUE")
            self.verticalGridLine([30,25],[30,17],"WHITE")
            self.grid[30][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.horizontalGridLine([30,17],[40,17],"WHITE")
            self.grid[40][17] = spreadBeaverNode(["WEST"],"UNLOCK","GREEN")
            self.verticalGridLine([30,17],[30,7],"GREEN")
            self.grid[30][7] = spreadBeaverNode(["SOUTH"],"UNLOCK","PINK")
            self.grid[30][17] = spreadBeaverNode(["SOUTH","NORTH","EAST","WEST"],False,"WHITE")
            self.grid[35][25] = spreadBeaverNode(["EAST","WEST"],True,"RED")
            self.grid[38][25] = spreadBeaverNode(["EAST","WEST"],True,"GREEN")
            self.grid[40][25] = spreadBeaverNode(["EAST","WEST"],True,"BLUE")
            self.grid[43][25] = spreadBeaverNode(["EAST","WEST"],True,"PINK")
            self.pos = [5,25]
            self.goalPos = [45,25]
            print "passed level 4"

        elif self.pos == [45,25]:
            self.clearGrid()
            self.verticalGridLine([47,30],[47,16],"WHITE")
            self.horizontalGridLine([0,16],[47,16],"WHITE")
            self.grid[47][16] = spreadBeaverNode(["WEST","SOUTH"],False,"WHITE")
            self.verticalGridLine([43,16],[43,25],"YELLOW")
            self.horizontalGridLine([36,25],[43,25],"YELLOW")
            self.grid[43][16] = spreadBeaverNode(["WEST","SOUTH","EAST"],False,"WHITE")
            self.grid[43][25] = spreadBeaverNode(["NORTH","WEST"],False,"YELLOW")
            self.verticalGridLine([30,16],[30,25],"GREEN")
            self.horizontalGridLine([30,25],[36,25],"GREEN")
            self.grid[36][25] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","PINK")
            self.grid[30][25] = spreadBeaverNode(["EAST","NORTH"],False,"GREEN")
            self.verticalGridLine([30,16],[30,5],"BLUE")
            self.horizontalGridLine([23,5],[30,5],"BLUE")
            self.grid[30][5] = spreadBeaverNode(["WEST","SOUTH"],False,"BLUE")
            self.grid[30][16] = spreadBeaverNode(["EAST","SOUTH","WEST","NORTH"],False,"WHITE")
            self.horizontalGridLine([19,5],[23,5],"WHITE")
            self.verticalGridLine([19,16],[19,5],"WHITE")
            self.grid[23][5] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","GREEN")
            self.grid[19][5] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.verticalGridLine([19,16],[19,25],"BLUE")
            self.horizontalGridLine([12,25],[19,25],"RED")
            self.grid[19][16] = spreadBeaverNode(["NORTH","SOUTH","EAST","WEST"],False,"WHITE")
            self.grid[19][25] = spreadBeaverNode(["WEST","NORTH"],"UNLOCK","BLUE")
            self.verticalGridLine([12,16],[12,25],"WHITE")
            self.grid[12][25] = spreadBeaverNode(["NORTH","EAST"],"UNLOCK","RED")
            self.verticalGridLine([12,16],[12,5],"PINK")
            self.horizontalGridLine([8,5],[12,5],"PINK")
            self.horizontalGridLine([6,5],[8,5],"WHITE")
            self.verticalGridLine([6,16],[6,5],"WHITE")
            self.grid[12][5] = spreadBeaverNode(["WEST","SOUTH"],False,"PINK")
            self.grid[12][16] = spreadBeaverNode(["NORTH","SOUTH","EAST","WEST"],False,"WHITE")
            self.grid[8][5] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","YELLOW")
            self.grid[6][5] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.grid[6][16] = spreadBeaverNode(["NORTH","EAST","WEST"],False,"WHITE")
            self.grid[5][16] = spreadBeaverNode(["EAST","WEST"],True,"YELLOW")
            self.grid[4][16] = spreadBeaverNode(["EAST","WEST"],True,"GREEN")
            self.grid[3][16] = spreadBeaverNode(["EAST","WEST"],True,"PINK")
            self.grid[2][16] = spreadBeaverNode(["EAST","WEST"],True,"RED")
            self.grid[1][16] = spreadBeaverNode(["EAST","WEST"],True,"BLUE")
            self.goalPos = [0,16]
            self.pos = [47,25]
            print "cleared level 5"
            
                
    def draw(self,screen):
        for i in range(len(self.grid)):
            for k in range(len(self.grid[i])):
                screen.blit(self.grid[i][k].drawSurface, (i * 20, k * 20))
                if self.grid[i][k].locked:
                    screen.blit(self.grid[i][k].drawSurface, (i * 20, k * 20))
        screen.blit(self.cursor, (self.pos[0] * 20, self.pos[1] * 20))
        screen.blit(self.goal, (self.goalPos[0] * 20, self.goalPos[1] * 20))

    def unlockGrid(self,color):
        for i in range(len(self.grid)):
            for k in range(len(self.grid[i])):
                self.grid[i][k].unlock(color)

    def clearGrid(self):
        for i in range(len(self.grid)):
            for k in range(len(self.grid[i])):
                self.grid[i][k] = spreadBeaverNode([],False,"WHITE")

    def horizontalGridLine(self,startPos,endPos,color):
        if startPos[0] > endPos[0]:
            temp = startPos
            startPos = endPos
            endPos = temp
            
        for i in range(endPos[0] - startPos[0]):
            self.grid[i + startPos[0]][startPos[1]] = spreadBeaverNode(["EAST","WEST"],False,color)

    def verticalGridLine(self,startPos,endPos,color):
        if startPos[1] > endPos[1]:
            temp = startPos
            startPos = endPos
            endPos = temp

        for i in range(endPos[1] - startPos[1]):
            self.grid[startPos[0]][i + startPos[1]] = spreadBeaverNode(["NORTH","SOUTH"],False,color)

class rocketDivePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideRocketDive.png', -1)
        self.velocity = [0,0]
        self.life = 100
        # [0] is horizontal movement, [1] is timer [2] is vertical movement [3] is the timer for that
        self.lastAction = [None,-1,None,-1]

    def update(self):
        keys = pygame.key.get_pressed()
        if self.lastAction[0] == "LEFT":
            if not keys[K_LEFT]:
                self.lastAction[1] = 3
        elif self.lastAction[0] == "RIGHT":
            if not keys[K_RIGHT]:
                self.lastAction[1] = 3
        if self.lastAction[2] == "DOWN":
            if not keys[K_DOWN]:
                self.lastAction[3] = 3
        elif self.lastAction[2] == "UP":
            if not keys[K_UP]:
                self.lastAction[3] = 3
        if keys[K_LEFT]:
            if self.lastAction[0] == "LEFT" and self.lastAction[1] >= 0:
                self.velocity[0] = -30
                self.lastAction[0] = None
            else:
                self.lastAction[0] = "LEFT"
                self.velocity[0] = -3
        elif keys[K_RIGHT]:
            if self.lastAction[0] == "RIGHT" and self.lastAction[1] >= 0:
                self.velocity[0] = 30
                self.lastAction[0] = None
            else:
                self.velocity[0] = 3
                self.lastAction[0] = "RIGHT"
        else:
            self.velocity[0] = 0
        if keys[K_DOWN]:
            if self.lastAction[2] == "DOWN" and self.lastAction[3] >= 0:
                self.velocity[1] = 30
                self.lastAction[2] = None
            else:
                self.velocity[1] = 3
                self.lastAction[2] = "DOWN"
        elif keys[K_UP]:
            if self.lastAction[2] == "UP" and self.lastAction[3] >= 0:
                self.velocity[1] = -30
                self.lastAction[2] = None
            else:
                self.velocity[1] = -3
                self.lastAction[2] = "UP"
        else:
            self.velocity[1] = 0
        self.lastAction[1] -= 1
        self.lastAction[3] -= 1
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

class rocketDiveMeteor(pygame.sprite.Sprite):
    def __init__(self, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('asteroid.png')
        self.rect.topleft = loc
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() + randint(-100, 100), self.image.get_height() + randint(-100,100)))

    def update(self,speed):
        self.rect.y -= speed
        if self.rect.bottom < 0:
            self.kill()

class rocketDivePowerUp(pygame.sprite.Sprite):
    def __init__(self,loc):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('bourbon.png')
        self.rect.center = loc

    def update(self,speed):
        self.rect.y -= speed
        if self.rect.bottom < 0:
            self.kill()
        
class leatherFacePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('hideLeatherFace.png', -1)
        self.originalImage = self.image
        self.lyingDownImage, temp = load_image('hideLeatherFaceLyingDown.png', -1)
        self.velocity = 0
        self.rect.y = 220
        self.rect.x = 100
        self.hiding = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and not self.hiding:
            self.velocity = -5
        elif keys[K_RIGHT] and not self.hiding:
            self.velocity = 5
        else:
            self.velocity = 0
        if keys[K_DOWN]:
            if not self.hiding:                    
                self.hiding = True
                self.image = self.lyingDownImage
                self.rect.y += 180
                self.image.set_alpha(100)
        elif keys[K_UP]:
            if not self.hiding:
                self.hiding = True
                self.image.set_alpha(100)
        else:
            if self.hiding:
                self.hiding = False
                if self.image == self.lyingDownImage:
                    self.image = self.originalImage
                    self.rect.y -= 180
                self.image.set_alpha(None)
                
        self.rect.x += self.velocity

    def hidingPosture(self):
        if self.hiding:
            if self.image is self.lyingDownImage:
                return "lyingDown"
            else:
                return "standing"
        else:
            return False

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
        self.timesSpotted = 0

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
        self.timesSpotted += 1

class leatherFaceObject(pygame.sprite.Sprite):
    def __init__(self,image, position, hideBox, hidingType):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image)
        self.rect.topleft = position
        self.hideBox = pygame.Rect(hideBox)
        self.hidingType = hidingType

    def checkHidingSpot(self,state,hitBox):
        if self.rect.colliderect(hitBox) and state == self.hidingType:
            return True
        else:
            return False

class pinkSpiderPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('pinkSpider.png', -1)
        self.originalImage = None
        self.rightWingStrength = 5
        self.leftWingStrength = 5
        self.velocity = [0,0]
        self.rect.x = 100
        self.rect.y = 500
        self.state = "grounded"

    def update(self):
        keys = pygame.key.get_pressed()
        if self.state == "grounded":
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
        else:
            if keys[K_LEFT]:
                self.velocity[2] = self.leftWingStrength
                self.leftWingStrength -= 0.05
            elif keys[K_RIGHT]:
                self.velocity[3] = self.rightWingStrength
                self.rightWingStrength -= 0.05
            else:
                if self.velocity[2] > -5:
                    self.velocity[2] -= 2
                if self.velocity[3] > -5:
                    self.velocity[3] -= 2

            self.velocity[1] = (self.velocity[2] + self.velocity[3]) * -1
            balance = self.velocity[2] - self.velocity[3]
            self.image = pygame.transform.rotate(self.originalImage, 5 * balance)
            self.velocity[0] = balance * 2
            
        self.rect.x += self.velocity[0]
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.width > 1000:
            self.rect.x = 1000 - self.rect.width
        self.rect.y += self.velocity[1]

    def transform(self):
        self.image, temp = load_image("pinkSpiderWings.png", -1)
        self.originalImage = self.image
        self.state = "flying"
        self.velocity = [self.velocity[0],self.velocity[1], 0, 0]

class pinkSpiderFly(pygame.sprite.Sprite):
    def __init__(self, bugType):
        pygame.sprite.Sprite.__init__(self)
        if bugType is "fly":                
            self.image, self.rect = load_image('fly.png', -1)
        else:
            self.image, self.rect = load_image('butterfly.png', -1)
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        self.rect.x = randint(0,1000)
        self.rect.y = randint(0,600)
        self.velocity = [5,0]
        self.caught = False
        self.frameTimer = 0
        self.bugType = bugType
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
        self.sprite.image, self.sprite.rect = load_image('doubtFrog.png', -1)
        self.originalImage = self.sprite.image.convert()
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
            if keys[K_UP]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, 135)
            elif keys[K_DOWN]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, 45)
            else:
                self.sprite.image = pygame.transform.rotate(self.originalImage, 90)
        elif keys[K_LEFT]:
            if self.slope['x'] > -6:
                self.slope['x'] -= 1
            if keys[K_UP]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, -135)
            elif keys[K_DOWN]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, -45)
            else:
                self.sprite.image = pygame.transform.rotate(self.originalImage, -90)
        else:
            if keys[K_UP]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, 180)
            elif keys[K_DOWN]:
                self.sprite.image = pygame.transform.rotate(self.originalImage, 0)
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
        self.image, self.rect = load_image("tadpole.png", -1)
        self.originalImage = self.image
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

        if self.velocity[1] > 0:
            self.image = pygame.transform.rotate(self.originalImage, 15 * self.velocity[0])
        else:
            self.image = pygame.transform.rotate(self.originalImage, 180 + (15 * self.velocity[0]))
            
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
        self.endLines = []

    def update(self):
        if self.state == "neutral":
            keys = pygame.key.get_pressed()
            if keys[K_UP]:
                self.state = "jumping"
                self.frameTimer = 40
            if keys[K_DOWN]:
                self.state = "submerged"
                self.frameTimer = 40
            self.speed += 0.01
        elif self.state is "jumping" or self.state == "submerged":
            self.frameTimer -= 1
            if self.frameTimer == 0:
                self.state = "neutral"
        elif self.state == "homeFree":
            self.frameTimer -= 1
            self.fishPic = pygame.transform.scale(self.fishPic,(self.frameTimer,self.frameTimer * 2))
            for i in self.endLines:
                i.next()
        return self.speed

    def draw(self, screen):
        if self.state is "neutral":
            if self.fishNum > 0:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic, True, False), - 25),(250, 500))
            if self.fishNum > 1:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic,True,False), -12), (380,520))
            if self.fishNum > 2:
                screen.blit(pygame.transform.rotate(self.fishPic, 12), (620,520))
            if self.fishNum > 3:
                screen.blit(pygame.transform.rotate(self.fishPic, 25), (750, 500))
        elif self.state is "jumping":
            if self.fishNum > 0:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic, True, False), - 25),(250, 400))
                screen.blit(self.fishShadow, (250,500))
            if self.fishNum > 1:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic,True,False), -12), (380,420))
                screen.blit(self.fishShadow, (380, 520))
            if self.fishNum > 2:
                screen.blit(pygame.transform.rotate(self.fishPic, 12), (620,420))
                screen.blit(self.fishShadow, (620, 520))
            if self.fishNum > 3:
                screen.blit(pygame.transform.rotate(self.fishPic, 25), (750, 400))
                screen.blit(self.fishShadow, (750, 500))
        elif self.state is "submerged":
            if self.fishNum > 0:
                screen.blit(self.fishShadow, (250,500))
            if self.fishNum > 1:
                screen.blit(self.fishShadow, (380, 520))
            if self.fishNum > 2:
                screen.blit(self.fishShadow, (620, 520))
            if self.fishNum > 3:
                screen.blit(self.fishShadow, (750, 500))
        elif self.state is "homeFree":
            if self.fishNum > 0:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic, True, False), - 25),self.endLines[0].pos)
            if self.fishNum > 1:
                screen.blit(pygame.transform.rotate(pygame.transform.flip(self.fishPic,True,False), -12), self.endLines[1].pos)
            if self.fishNum > 2:
                screen.blit(pygame.transform.rotate(self.fishPic, 12), self.endLines[2].pos)
            if self.fishNum > 3:
                screen.blit(pygame.transform.rotate(self.fishPic, 25), self.endLines[3].pos)

    def gameOverKa(self, obstacle):
        print "gameOverKa with argument: ", obstacle
        if obstacle is "log":
            if self.state is "jumping":
                return False
            else:
                self.fishNum -= 1
                if self.fishNum <= 0:
                    return True
                else:
                    return False
        elif obstacle is "bear":
            if self.state is "submerged":
                return False
            else:
                
                self.fishNum -= 1
                if self.fishNum <= 0:
                    return True
                else:
                    return False

    def beFree(self):
        if self.state is "homeFree":
            self.frameTimer -= 1
        else:
            self.state = "homeFree"
            self.frameTimer = 40
            if self.fishNum > 0:
                self.endLines.append( Interpolator((250, 500),(500,300),0.7,60))
            if self.fishNum > 1:
                self.endLines.append(Interpolator((380,520),(500,300),0.7,60))
            if self.fishNum > 2:
                self.endLines.append(Interpolator((620,520),(500,300),0.7,60))
            if self.fishNum > 3:
                self.endLines.append(Interpolator((750,500),(500,300),0.7,60))
            
        
class fishScratchFeverObstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        typeList = {0:"log",1:"bear",2:"food",3:"Dam"}
        self.type = typeList[randint(0,3)]
        self.distance = 100
        if self.type == "log":
            self.image, self.rect = load_image("log.png", -1)
            self.rect.topleft = (470, 340)
        elif self.type == "bear":
            self.image, self.rect = load_image("bear.png", -1)
            self.rect.topleft = (200, 230)
        else:
            self.image, self.rect = load_image("log.png", -1)
            self.type = "log"
            self.rect.topleft = (470, 340)
        self.originalImage = self.image

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
        if self.type is "log":
            self.rect.centerx = 500
        if self.type is "bear":
            self.rect.centerx -= 5

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
        
        self.rect = self.rect.move(self.slope[0] * self.velocity[0] * 1.5, self.slope[1] * self.velocity[1] * 1.5)
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
        if self.slope[1] < 0:
            self.slope = [5,5]
        self.image, temp = load_image("breedingHide.png", -1)
        
class everFreeSurface():
    def __init__(self,slope,position,drag,length, velocityProfile):
        self.slope = slope
        self.position = position
        self.drag = drag
        self.velocityProfile = [False,False]
        self.length = length
        self.lineCoords = []
        if slope[0] == 0:
            self.drawSurface = pygame.Surface((5,length))
        else:
            self.drawSurface = pygame.Surface((length, (length / slope[0]) * abs(slope[1])))
        self.drawSurface = self.drawSurface.convert()
        self.drawSurface.fill((0,0,0))
        if slope[0] == 0:
            pygame.draw.line(self.drawSurface,(250,250,250), (0,0),(0,self.drawSurface.get_height()))
        elif slope[1] < 0:
            pygame.draw.line(self.drawSurface,(250,250,250),(0,self.drawSurface.get_height()),(self.length,0))
            self.assignLineCoords()
        else:
            pygame.draw.line(self.drawSurface,(250,250,250),(0,0),(self.length,self.drawSurface.get_height()))
            self.assignLineCoords()

    def assignLineCoords(self):
        pixelArray = pygame.PixelArray(self.drawSurface)
        for i in range(self.drawSurface.get_width()):
            for k in range(self.drawSurface.get_height()):
                if pixelArray[i][k] == self.drawSurface.map_rgb((250,250,250)):
                    self.lineCoords.append((i + self.position[0],k + self.position[1]))

    def draw(self,screen):
        screen.blit(self.drawSurface,self.position)

    def collideableRect(self):
        return self.drawSurface.get_rect().move(self.position)

    def returnHeight(self,x):
        x -= self.position[0]
        if self.slope[0] == 0:
            return x
        elif self.slope[1] < 0:
            return (x * (float(self.slope[1]) / self.slope[0]) + self.drawSurface.get_height() + self.position[1])
        else:
            return (x * (float(self.slope[1]) / self.slope[0])) + self.position[1]

    def canAttach(self,rect):
        # If the slope is 0, intersecting the rect is good enough test
        if self.slope[0] == 0:
            return True
        for i in self.lineCoords:
            if rect.collidepoint(i):
                return True
        return False

class everFreeLava():
    def __init__(self,dimensions):
        self.rect = pygame.Rect(dimensions)
        self.image = pygame.Surface((self.rect.width,self.rect.height))
        self.image = self.image.convert()
        self.image.fill((250,0,0))
        print self.image

    def update(self):
        self.rect.h += 0.5
        self.rect.y -= 0.5
        self.image = pygame.Surface((self.rect.width,self.rect.height))
        self.image = self.image.convert()
        self.image.fill((250,0,0))
    
class breedingGrid():
    def __init__(self):
        self.player = breedingPlayer(self)
        self.goal = pygame.sprite.Sprite()
        self.goal.image, self.goal.rect = load_image("magmaBall.png")
        self.goal.rect.topleft = (900,50)
        self.columns = []
        self.NUMCOLUMNS = 10
        self.numBugs = 0
        self.bugs = None
        self.bugInterpolator = None
        for i in range(self.NUMCOLUMNS):
            self.columns.append(breedingColumn(i))

    def update(self):
        for i in self.columns:
            i.update()
        if self.bugs:
            self.bugs.rect.midbottom = self.bugInterpolator.pos
            self.bugInterpolator.next()

    def draw(self,screen):
        for i in range(self.NUMCOLUMNS):
            self.columns[i].drawColumn(screen)
        if self.player.carrying:
            pygame.draw.rect(screen,(250,0,0),pygame.Rect(self.player.rect.left,self.player.rect.top - 100, 100, 100))
        if self.bugs:
            screen.blit(self.bugs.image, self.bugs.rect.topleft)
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
                    theBlock = self.columns[position + 1].removeBlock()
                    self.numBugs += 1
                    self.updateBugs()
                    return theBlock
                elif action is "drop":
                    self.columns[position + 1].addBlock(self.player.carrying)
                    self.updateBugs()
                    return True
                else:
                    return False
            else:
                return False
        elif position > 0:
            if abs(self.columns[position].height - self.columns[position -1].height) <= 1:
                if action is "pickup" and self.columns[position -1].height > 0:
                    theBlock = self.columns[position -1].removeBlock()
                    self.numBugs += 1
                    self.updateBugs()
                    return theBlock
                elif action is "drop":
                    self.columns[position -1].addBlock(self.player.carrying)
                    return True
                else:
                    return False
            else:
                return False

    def updateBugs(self):
        largest = breedingColumn(0)
        for i in self.columns:
            i.numBugs = 0
            if i.totalHeight() >= largest.totalHeight():
                largest = i
        largest.numBugs = self.numBugs
        if self.bugs is None:
            self.bugs = pygame.sprite.Sprite()
            self.bugs.image, self.bugs.rect = load_image("ant.png",-1)
            self.bugs.rect.midbottom = self.player.rect.midbottom
            self.bugInterpolator = Interpolator(self.player.rect.bottomleft,((largest.number+1) * 100,600),1,60)
        else:
            self.bugInterpolator = Interpolator(self.bugs.rect.midbottom,((largest.number+1) * 100,600),1,60)


class breedingColumn():
    def __init__(self, number, height=0):
        self.height = height
        self.occupied = False
        self.number = number
        self.numBugs = 0
        self.blocks = []

    def update(self):
        if len(self.blocks) > 0 and self.numBugs:
            self.blocks[0].height -= (0.005 * self.numBugs)
            if self.blocks[0].height <= 0:
                self.blocks.pop(0)

    def addBlock(self,theBlock):
        if theBlock is False:
            print "false block being added"
        self.height += 1
        self.blocks.append(theBlock)
        
    def removeBlock(self):
        if self.height > 0:
            self.height -= 1
            return self.blocks.pop(-1)
        
    def drawColumn(self,screen):
        lastY = 600
        for i in self.blocks:
            pygame.draw.rect(screen, (250,0,0), pygame.Rect((self.number + 1) * 100, lastY-i.height,100,100))
            lastY = lastY-i.height

    def changeHeight(self, num):
        self.height = num
        for i in range(self.height):
            self.blocks.append(breedingBlock())

    def totalHeight(self):
        theSum = 0
        for i in self.blocks:
            theSum += i.height
        return theSum

class breedingBlock():
    def __init__(self,height=100):
        self.height = height
        

class breedingPlayer(pygame.sprite.Sprite):
    def __init__(self, grid):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('breedingHide.png',-1)
        self.carrying = False
        self.facingRight = True
        self.image = pygame.transform.flip(self.image, True, False)
        self.locked = False
        self.grid = grid
        self.position = 4
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
                    self.carrying = self.grid.allowAction(self.position, self.facingRight, "pickup")
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
        self.footPrintTimer =  20
        self.jumpTimer = 0

    def update(self):
        self.rect.x += 5
        self.footPrintTimer -= 1
        if self.footPrintTimer < 0:
            self.footPrintTimer = 20
        if self.jumpTimer:
            self.rect.y = 400
            self.jumpTimer -= 1
        else:
            keys = pygame.key.get_pressed()
            if keys[K_DOWN]:
                self.rect.y = 550
            elif keys[K_UP]:
                self.jumpTimer = 20
            else:
                self.rect.y = 500

    def draw(self,screen):
        screen.blit(self.image, (10 + self.offset,self.rect.y))

class hurryGoRoundObstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image,self.rect = load_image("leatherFaceTarget.png",-1)
        self.rect.x = 1100
        self.rect.y = 550

    def update(self):
        self.rect.x -= 5

    def draw(self,screen,offset,x):
        screen.blit(self.image,(self.rect.x - x,self.rect.y))

class hurryGoRoundFootprint(pygame.sprite.Sprite):
    def __init__(self,position,flipped):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("footPrint.png", -1)
        self.image = pygame.transform.flip(self.image,False,flipped)
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

def changeTrack(direction,gameData):
    gameData['spriteList'].empty()
    if direction is "BACK":
        if gameData['trackFrameCounter'] > 0:
            gameData['trackNumber'] -= 2
            gameData['trackFrameCounter'] = 50
        else:
            gameData['trackNumber'] -= 1
            gameData['trackFrameCounter'] = 50
    # Change track to Rocket Dive
    if gameData['trackNumber'] == 1:
        gameData['player'] = rocketDivePlayer()
        gameData['spriteList'].add(gameData['player'])
        gameData['frameCounter'] = 100
    # Change track to Leather Face
    if gameData['trackNumber'] == 2:
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        pygame.draw.polygon(newBackground,(200,200,200),[(0,200),(1000,200),(1000,500),(0,500)])
        gameData['backGround'] = newBackground
        gameData['player'] = leatherFacePlayer()
        gameData['leatherFaceObjects'] = pygame.sprite.Group(leatherFaceObject('door.png',(400,220),(400,220,100,250),"standing"))
        gameData['leatherFaceObjects'].add(leatherFaceObject('bookshelf.png',(1000,200),(800,200,120,300),"standing"))
        gameData['spriteList'].add(gameData['player'],leatherFaceTarget(), gameData['leatherFaceObjects'])
        gameData['frameCounter'] = 0
    # Change track to Pink Spider
    elif gameData['trackNumber'] == 3:
        gameData['player'] = pinkSpiderPlayer()
        gameData['spriteList'].add(gameData['player'])
        gameData['backGround'], temp = load_image('spiderweb.png')
        gameData['bouncingRect'] = pygame.Rect(0,590,1000,10)
        gameData['bounces'] = 0
    # Change track to Doubt '97
    elif gameData['trackNumber'] == 4:
        gameData['player'] = doubtPlayer()
        for i in range(6):
            gameData['spriteList'].add(doubtEnemy())
        newBackground = pygame.Surface((10000,6000))
        newBackground = newBackground.convert()
        #newBackground.fill((0,0,0),)
        red = 67
        green = 233
        blue = 41
        for i in [0,600,1200,1800,2400,3000,3600,4200,4800,5400,6000]:
            newBackground.fill((red,green,blue),pygame.Rect(0,i,10000,600))
            red -= 5
            green -= 20
            blue -= 3
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
        gameData['frameCounter'] = 130
        gameData['targetDistance'] = 1000
    # Change track to Ever Free
    elif gameData['trackNumber'] == 6:
        gameData['player'] = everFreePlayer()
        gameData['player'].rect.center = (1800,1900)
        gameData['sideScrollingSurface'] = pygame.Surface((3000,3000))
        gameData['surfaces'] = [everFreeSurface([10,3],(300,100),1,550,[True,False])]
        gameData['surfaces'].append(everFreeSurface([0,5],(1100,400),1,200,[False,False]))
        gameData['surfaces'].append(everFreeSurface([10,-3],(1300,100),1,550,[True,False]))
        gameData['surfaces'].append(everFreeSurface([0,5],(1900,0),1,500,[False,False]))
        gameData['surfaces'].append(everFreeSurface([0,5],(1700,500),1,200,[False,False]))
        gameData['surfaces'].append(everFreeSurface([1,3],(900,700),1,300,[True,False]))
        gameData['surfaces'].append(everFreeSurface([3,-4],(500,800),1,250,[True,False]))
        gameData['surfaces'].append(everFreeSurface([1,3],(200,1000),1,350,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(1300,1100),1,500,[True,False]))
        gameData['surfaces'].append(everFreeSurface([0,5],(1900,1100),1,300,[False,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(700,1400),1,300,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,-3],(1300,1400),1,500,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(1100,1600),1,300,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(400,1700),1,200,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(1000,1800),1,400,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(1800,1800),1,200,[True,False]))
        gameData['surfaces'].append(everFreeSurface([5,0],(0,1920),1,200,[True,False]))
        gameData['surfaces'].append(everFreeSurface([12,3],(600,2000),1,600,[True,False]))
        gameData['surfaces'].append(everFreeSurface([12,-3],(1500,2000),1,600,[True,False]))
        gameData['goal'] = pygame.Rect(0,0,100,450)
        gameData['lava'] = everFreeLava((-100,3000,2000,1))
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        gameData['backGround'] = newBackground
    # Change track to Breeding
    elif gameData['trackNumber'] == 7:
        gameData['grid'] = breedingGrid()
        gameData['grid'].columns[0].changeHeight(4)
        gameData['grid'].columns[1].changeHeight(3)
        gameData['grid'].columns[2].changeHeight(2)
        gameData['grid'].columns[3].changeHeight(1)
        gameData['player'] = gameData['grid'].player
        gameData['spriteList'].add(gameData['player'])
        gameData['backGround'].fill((0,0,0))
    # Change track to Hurry Go Round
    elif gameData['trackNumber'] == 8:
        gameData['player'] = hurryGoRoundPlayer()
        gameData['spriteList'].add(gameData['player'],hurryGoRoundObstacle())
        gameData['flipped'] = False
        gameData['frameCounter'] = 100
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
    gameData = {'player': None,'trackNumber':trackNumber,'spriteList':allsprites,'background':background,'distance':1000, 'trackFrameCounter':0}
    distanceTracker = pygame.font.Font(None, 36)
    sideScrollingSurface = pygame.Surface(screen.get_size())
    sideScrollingSurface = sideScrollingSurface.convert()
    sideScrollingSurface.fill((0,0,0))

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
                changeTrack("FORWARD",gameData)
            elif event.type == KEYDOWN and event.key == K_o:
                allsprites.empty()
                changeTrack("BACK",gameData)

        screen.blit(background, (0,0))
        # ----- Track 1, Spread Beaver -----
        if gameData['trackNumber'] == 1:
            grid.update()
            grid.draw(screen)
            if grid.pos == grid.goalPos:
                changeTrack("FORWARD",gameData)
        # ----- Track 2, Rocket Dive -------
        elif gameData['trackNumber'] == 2:
            frameTimer -= 1

            speed += 0.005
            gameData['distance'] -= (speed / 50)
            
            if frameTimer == 0:
                if randint(0,10) < 9:
                    meteors.add(rocketDiveMeteor((randint(0,1000),600)))
                else:
                    meteors.add(rocketDivePowerUp((randint(0,1000),600)))
                frameTimer = 30 + randint(-3,20)
            for i in meteors.sprites():
                if gameData['player'].rect.colliderect(i.rect):
                    if type(i) is rocketDiveMeteor:                            
                        gameData['player'].life -= 10
                        player1LifeMeter.update(gameData['player'].life)
                    else:
                        gameData['player'].life += 10
                        player1LifeMeter.update(gameData['player'].life)
                    i.kill()
                    if gameData['player'].life == 0:
                        changeTrack("FORWARD",gameData)
                        meteors.empty()
                        break
            meteors.update(speed)
            meteors.draw(screen)
            if gameData['distance'] <= 0:
                meteors.empty()
                allsprites.empty()
                gameData['frameCounter'] -= 1
                screen.blit(distanceTracker.render("Sail Away!", 1, (200,10,10)), (500,300))
                if gameData['frameCounter'] <= 0:
                    changeTrack("FORWARD",gameData)
            else:
                screen.blit(distanceTracker.render(str(gameData['distance']), 1, (200,10,10)), (900,500))
            player1LifeMeter.draw(screen)
            
        # ----- Track 3, Leather Face -------
        elif gameData['trackNumber'] == 3:
            allsprites = gameData['spriteList']
            screen.blit(gameData['backGround'], (0,0))
            for i in gameData['spriteList'].sprites():
                if gameData['frameCounter'] == 0:
                    if type(i) == leatherFaceObject:
                        i.rect.x += -1 * gameData['player'].velocity
                    elif type(i) == leatherFaceTarget:
                        i.rect.x += -1 * gameData['player'].velocity
                        if i.rect.colliderect(gameData['player'].rect):
                            i.runAway()
                            if i.timesSpotted == 3:
                                changeTrack("FORWARD",gameData)
                                frameTimer = 50
                            gameData['frameCounter'] = 40
                        if not i.facingRight:
                            if not gameData['player'].hiding:
                                changeTrack("FORWARD",gameData)
                                frameTimer = 50
                                break
                            else:
                                visible = True
                                for i in gameData['leatherFaceObjects']:
                                    if i.checkHidingSpot(gameData['player'].hidingPosture(),gameData['player'].rect):
                                        visible = False
                                        break
                                if visible:
                                    changeTrack("FORWARD",gameData)
                                    frameTimer = 50
                                    break
                else:
                    i.rect.x -= 5
            if gameData['frameCounter'] > 0:
                gameData['frameCounter'] -= 1
        # ----- Track 4, Pink Spider -------
        elif gameData['trackNumber'] == 4:
            allsprites = pygame.sprite.Group()
            sideScrollingSurface.blit(gameData['backGround'], (0,0))
            frameTimer -= 1
            if frameTimer == 0:
                if randint(0,5) == 1:
                    gameData['spriteList'].add(pinkSpiderFly("butterfly"))
                else:
                    gameData['spriteList'].add(pinkSpiderFly("fly"))
                frameTimer = 200
            for i in gameData['spriteList'].sprites():
                if type(i) != pinkSpiderPlayer and gameData['player'].rect.colliderect(i.rect):
                    i.getCaught()
                    if i.bugType is not "fly":
                        gameData['player'].transform()
                        gameData['spriteList'].remove(gameData['player'])
            gameData['spriteList'].update()
            gameData['spriteList'].draw(sideScrollingSurface)
            sideScrollingOffset = gameData['player'].velocity
            if gameData['player'].state == "grounded":
                screen.blit(sideScrollingSurface, (0,0))
            else:
                if gameData['player'].rect.colliderect(gameData['bouncingRect']) and gameData['bounces'] < 3:
                    gameData['player'].leftWingStrength = 10
                    gameData['player'].rightWingStrength = 10
                    gameData['bounces'] += 1
                gameData['player'].update()
                screen.blit(sideScrollingSurface, (500 - gameData['player'].rect.x,300 - gameData['player'].rect.y))
                screen.blit(gameData['player'].image, (500,300))
                if gameData['player'].rect.y > 600:
                    changeTrack("FORWARD",gameData)
        # ----- Track 5, Doubt '97 -----
        elif gameData['trackNumber'] == 5:
            allsprites = pygame.sprite.Group()
            #screen.blit(gameData['backGround'], (0,0))
            gameData['spriteList'].update()
            gameData['player'].update()
            offset = gameData['player'].offset
            screen.blit(gameData['backGround'], (-5000 - offset[0],-2000 + offset[1]))
            screen.blit(gameData['player'].sprite.image, (500,300))
            for i in gameData['spriteList'].sprites():
                screen.blit(i.image, (i.rect.x - offset[0], i.rect.y + offset[1]))
                if i.rect.colliderect(gameData['player'].sprite.rect):
                    i.kill()
                    gameData['player'].eat()
            if gameData['player'].sprite.rect.width < 5:
                changeTrack("FORWARD",gameData)
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
                        changeTrack("FORWARD",gameData)
            gameData['frameCounter'] -= 1
            gameData['targetDistance'] -= curSpeed
            if gameData['frameCounter'] == 0 and gameData['targetDistance'] > 0:
                gameData['spriteList'].add(fishScratchFeverObstacle())
                gameData['frameCounter'] = 130
            if gameData['targetDistance'] <= 0:
                gameData['player'].beFree()
                if gameData['player'].frameTimer <= 0:
                    changeTrack("FORWARD",gameData)
        # ----- Track 7, Ever Free -----
        elif gameData['trackNumber'] == 7:
            gameData['sideScrollingSurface'].blit(gameData['backGround'], (0,0))
            for i in gameData['surfaces']:
                i.draw(gameData['sideScrollingSurface'])
                if not gameData['player'].unattachableTime:                        
                    if i != gameData['player'].touchingSurface:
                        if gameData['player'].rect.colliderect(i.collideableRect()):
                            if i.canAttach(gameData['player'].rect):
                                gameData['player'].attachToSurface(i)
                    else:
                        if not gameData['player'].rect.colliderect(i.collideableRect()):
                            gameData['player'].detachFromSurface([0,6])
            gameData['lava'].update()
            gameData['player'].update()
            if gameData['player'].rect.colliderect(gameData['goal']):
                changeTrack("FORWARD",gameData)
            if gameData['player'].rect.colliderect(gameData['lava'].rect):
                print "lava"
                changeTrack("FORWARD",gameData)
            gameData['sideScrollingSurface'].blit(gameData['lava'].image, (gameData['lava'].rect.x,gameData['lava'].rect.y))
            screen.blit(gameData['sideScrollingSurface'], (500 - gameData['player'].rect.x,300 - gameData['player'].rect.y))
            screen.blit(gameData['player'].image, (500,300))
        # ----- Track 8, Breeding ------
        elif gameData['trackNumber'] == 8:
            screen.blit(gameData['background'], (0,0))
            gameData['grid'].update()
            gameData['grid'].draw(screen)
        # ----- Track 9 Hurry Go Round -----
        elif gameData['trackNumber'] == 9:
            allsprites = pygame.sprite.Group()
            screen.blit(gameData['background'], (0,0))
            gameData['frameCounter'] -= 1
            if gameData['frameCounter'] <= 0:
                gameData['spriteList'].add(hurryGoRoundObstacle())
                gameData['frameCounter'] = randint(100,600)
            if gameData['player'].footPrintTimer == 0:
                gameData['spriteList'].add(hurryGoRoundFootprint(gameData['player'].rect.bottomleft,gameData['flipped']))
                gameData['flipped'] = not gameData['flipped']
                gameData['player'].footPrintTimer = 20
            gameData['spriteList'].update()
            for i in gameData['spriteList'].sprites():
                if type(i) is hurryGoRoundPlayer:
                    i.draw(screen)
                else:
                    if type(i) is hurryGoRoundObstacle and gameData['player'].rect.colliderect(i.rect):
                        gameData['player'].offset += 10
                        i.kill()
                        if gameData['player'].offset == 100:
                            print "you would lose here"
                    i.draw(screen,gameData['player'].offset,gameData['player'].rect.x)
            
        allsprites.update()
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
