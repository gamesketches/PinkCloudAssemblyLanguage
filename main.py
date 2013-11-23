import pygame, sys, os, math
from pygame.locals import *
from random import randint
from random import choice
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
            self.drawSurface, temp = load_image("redLock.png",-1)
        elif color is "GREEN":
            self.color = (0,250,0)
            self.drawSurface, temp = load_image("greenLock.png",-1)
        elif color is "BLUE":
            self.color = (0,0,250)
            self.drawSurface, temp = load_image("blueLock.png",-1)
        elif color is "PURPLE":
            self.color = (128,0,128)
            self.drawSurface, temp = load_image("purpleLock.png",-1)
        elif color is "YELLOW":
            self.color = (255,255,0)
        else:
            self.color = (255,255,255)
        if lock is False:
            self.locked = False
            self.drawSurface.fill((0,0,0))
            self.drawLines()
            if len(directions) == 0:
                self.locked = True
        elif lock is "UNLOCK":
            self.locked = "UNLOCK"
            self.drawSurface.fill(self.color)
        else:
            self.locked = True
            
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

    def deadOnTheWater(self):
        x = self.pos[0]
        y = self.pos[1]
    #    if self.grid[x+1][y].locked or not self.grid[x+1][y].hasDirection("EAST"):
   #         if self.grid[x-1][y].locked or not self.grid[x-1][y].hasDirection("WEST"):
  #              if self.grid[x][y+1].locked or not self.grid[x][y+1].hasDirection("NORTH"):
 #                   if self.grid[x][y-1].locked or not self.grid[x][y-1].hasDirection("SOUTH"):
#                        return True
        return False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            if self.cursorMovement[0] == "EAST":
                if self.cursorMovement[1] >= 4:
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
                if self.cursorMovement[1] >= 4:                            
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
                if self.cursorMovement[1] >= 4:                            
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
                if self.cursorMovement[1] >= 4:                            
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

        if self.pos == [1,15]:
            self.clearGrid()
            for i in xrange(30):
                self.grid[25][i] = spreadBeaverNode(["NORTH","SOUTH"], False, "WHITE")
            self.pos = [25,6]
            self.goalPos = [25,5]
            self.grid[25][26] = spreadBeaverNode(["NORTH","SOUTH"],True,"BLUE")
            
        if self.pos == [25,5] or self.pos == [48,29]:
            self.clearGrid()
            self.horizontalGridLine([0,15],[50,15],"WHITE")
            self.verticalGridLine([15,8],[15,15],"WHITE")
            self.horizontalGridLine([15,8],[40,8],"WHITE")
            self.grid[15][15] = spreadBeaverNode(["NORTH","WEST","EAST"], False, "WHITE")
            self.grid[15][8] = spreadBeaverNode(["EAST","SOUTH"],False,"WHTIE")
            self.grid[40][15] = spreadBeaverNode(["WEST","EAST"],True,"BLUE")
            self.grid[39][8] = spreadBeaverNode(["WEST"],"UNLOCK","BLUE")
            if self.pos == [25,5]:
                self.pos = [2,15]
            else:
                self.pos = [44,15]
            self.goalPos = [45,15]
            print "Passed level 1"
            
        elif self.pos == [45,15] or self.pos == [49,26]:
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
            if self.pos == [45,15]:
                self.pos = [48,28]
            else:
                self.pos = [6,20]
            self.goalPos = [5,20]
            print "Passed level 2"

        elif self.pos == [5,20] or self.pos == [4,25]:
            self.clearGrid()
            self.horizontalGridLine([24,26],[50,26],"WHITE")
            self.verticalGridLine([24,0],[24,26],"WHITE")
            self.grid[24][26] = spreadBeaverNode(["EAST","NORTH"],False,"WHITE")
            self.horizontalGridLine([6,20],[24,20],"WHITE")
            self.grid[6][20] = spreadBeaverNode(["EAST"],"UNLOCK","PURPLE")
            self.grid[24][20] = spreadBeaverNode(["WEST","NORTH","SOUTH"],False,"WHITE")
            self.horizontalGridLine([24,15],[40,15],"WHITE")
            self.grid[24][15] = spreadBeaverNode(["EAST","NORTH","SOUTH"],False,"WHTIE")
            self.grid[40][15] = spreadBeaverNode(["WEST"],"UNLOCK","GREEN")
            self.horizontalGridLine([24,10],[4,10],"PURPLE")
            self.grid[24][10] = spreadBeaverNode(["WEST","SOUTH","NORTH"],False,"WHITE")
            self.grid[4][10] = spreadBeaverNode(["EAST"],"UNLOCK","BLUE")
            self.grid[20][10] = spreadBeaverNode(["EAST","WEST"],False,"PURPLE")
            self.grid[24][5] = spreadBeaverNode(["NORTH","SOUTH"],True,"GREEN")
            self.grid[24][7] = spreadBeaverNode(["NORTH","SOUTH"],True,"PURPLE")
            self.grid[24][8] = spreadBeaverNode(["NORTH","SOUTH"],True,"BLUE")
            if self.pos == [5,20]:
                self.pos = [48,26]
            else:
                self.pos = [24,3]
            self.goalPos = [24,2]
            print "passed level 3"

        elif self.pos == [24,2] or self.pos == [47,27]:
            self.clearGrid()
            self.horizontalGridLine([0,25],[50,25],"WHITE")
            self.verticalGridLine([10,25],[10,17],"WHITE")
            self.horizontalGridLine([10,17],[15,17],"WHITE")
            self.verticalGridLine([15,25],[15,17],"WHITE")
            self.grid[10][17] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.grid[10][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.grid[15][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.verticalGridLine([15,16],[15,7],"PURPLE")
            self.grid[15][7] = spreadBeaverNode(["SOUTH"],"UNLOCK","RED")
            self.horizontalGridLine([15,17],[20,17],"RED")
            self.grid[15][17] = spreadBeaverNode(["EAST","WEST","NORTH","SOUTH"],False,"WHITE")
            self.grid[16][17] = spreadBeaverNode(["EAST","WEST"],False,"RED")
            self.grid[15][16] = spreadBeaverNode(["SOUTH","NORTH"],False,"PURPLE")
            self.grid[20][17] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","BLUE")
            self.horizontalGridLine([21,17],[30,17],"BLUE")
            self.grid[21][17] = spreadBeaverNode(["EAST","WEST"],False,"BLUE")
            self.verticalGridLine([30,25],[30,17],"WHITE")
            self.grid[30][25] = spreadBeaverNode(["EAST","WEST","NORTH"],False,"WHITE")
            self.horizontalGridLine([30,17],[40,17],"WHITE")
            self.grid[40][17] = spreadBeaverNode(["WEST"],"UNLOCK","GREEN")
            self.verticalGridLine([30,17],[30,7],"GREEN")
            self.grid[30][7] = spreadBeaverNode(["SOUTH"],"UNLOCK","PURPLE")
            self.grid[30][17] = spreadBeaverNode(["SOUTH","NORTH","EAST","WEST"],False,"WHITE")
            self.grid[35][25] = spreadBeaverNode(["EAST","WEST"],True,"RED")
            self.grid[38][25] = spreadBeaverNode(["EAST","WEST"],True,"GREEN")
            self.grid[40][25] = spreadBeaverNode(["EAST","WEST"],True,"BLUE")
            self.grid[43][25] = spreadBeaverNode(["EAST","WEST"],True,"PURPLE")
            if self.pos == [24,2]:
                self.pos = [5,25]
            else:
                self.pos = [44,25]
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
            self.grid[36][25] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","PURPLE")
            self.grid[30][25] = spreadBeaverNode(["EAST","NORTH"],False,"GREEN")
            self.verticalGridLine([30,16],[30,6],"BLUE")
            self.horizontalGridLine([23,6],[30,6],"BLUE")
            self.grid[30][6] = spreadBeaverNode(["WEST","SOUTH"],False,"BLUE")
            self.grid[30][16] = spreadBeaverNode(["EAST","SOUTH","WEST","NORTH"],False,"WHITE")
            self.horizontalGridLine([19,6],[23,6],"WHITE")
            self.verticalGridLine([19,16],[19,6],"WHITE")
            self.grid[23][6] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","GREEN")
            self.grid[19][6] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.verticalGridLine([19,16],[19,25],"BLUE")
            self.horizontalGridLine([12,25],[19,25],"RED")
            self.grid[19][16] = spreadBeaverNode(["NORTH","SOUTH","EAST","WEST"],False,"WHITE")
            self.grid[19][25] = spreadBeaverNode(["WEST","NORTH"],"UNLOCK","BLUE")
            self.verticalGridLine([12,16],[12,25],"WHITE")
            self.grid[12][25] = spreadBeaverNode(["NORTH","EAST"],"UNLOCK","RED")
            self.verticalGridLine([12,16],[12,5],"PURPLE")
            self.horizontalGridLine([8,5],[12,5],"PURPLE")
            self.horizontalGridLine([6,5],[8,5],"WHITE")
            self.verticalGridLine([6,16],[6,5],"WHITE")
            self.grid[12][5] = spreadBeaverNode(["WEST","SOUTH"],False,"PURPLE")
            self.grid[12][16] = spreadBeaverNode(["NORTH","SOUTH","EAST","WEST"],False,"WHITE")
            self.grid[8][5] = spreadBeaverNode(["EAST","WEST"],"UNLOCK","YELLOW")
            self.grid[6][5] = spreadBeaverNode(["EAST","SOUTH"],False,"WHITE")
            self.grid[6][16] = spreadBeaverNode(["NORTH","EAST","WEST"],False,"WHITE")
            self.grid[5][16] = spreadBeaverNode(["EAST","WEST"],True,"YELLOW")
            self.grid[4][16] = spreadBeaverNode(["EAST","WEST"],True,"GREEN")
            self.grid[3][16] = spreadBeaverNode(["EAST","WEST"],True,"PURPLE")
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
        if self.rect.x <= 0:
            self.rect.x = 0
        elif self.rect.right >= 1000:
            self.rect.right = 1000
        self.rect.y += self.velocity[1]
        if self.rect.y <= 0:
            self.rect.y = 0
        elif self.rect.bottom >= 600:
            self.rect.bottom = 600

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
        self.image, self.rect = load_image('bourbon.png',-1)
        self.rect.center = loc

    def update(self,speed):
        self.rect.y -= speed
        if self.rect.bottom < 0:
            self.kill()

class rocketDiveMissile(pygame.sprite.Sprite):
    def __init__(self,loc):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('missile.png', -1)
        self.rect.topleft = loc
        self.originalImage = self.image
        self.velocity = [1,0]
        self.frameTimer = 5

    def update(self,playerPos):
        if self.frameTimer == 0:
            turnRate = 5 * math.pi / 180
            objectDirection = self.velocity
            targetVector = [playerPos[0] - self.rect.x,playerPos[1] - self.rect.y]
            dotProduct = self.velocity[1] * targetVector[0] - self.velocity[0] * targetVector[1]
            if dotProduct > 0:
                tempx = math.cos(turnRate) * objectDirection[0] - math.sin(turnRate) * objectDirection[1]
                tempy = math.cos(turnRate) * objectDirection[1] + math.sin(turnRate) * objectDirection[0]
                objectDirection[0] = tempx
                objectDirection[1] = tempy
            elif dotProduct < 0:
                tempx = math.cos(-turnRate) * objectDirection[0] - math.sin(-turnRate) * objectDirection[1]
                tempy = math.cos(-turnRate) * objectDirection[1] + math.sin(-turnRate) * objectDirection[0]
                objectDirection[0] = tempx
                objectDirection[1] = tempy
            self.image = pygame.transform.rotate(self.originalImage, math.degrees(math.atan2(objectDirection[1],objectDirection[0]) * -1))
            self.velocity[0] = targetVector[0] / 200
            if abs(self.velocity[0]) < 3 and self.velocity[0] != 0:
                if self.velocity[0] > 0:
                    self.velocity[0] = 3
                else:
                    self.velocity[0] = -3
            self.velocity[1] = targetVector[1] / 200
            if abs(self.velocity[1]) < 3 and self.velocity[1] != 0:
                if self.velocity[1] > 0:
                    self.velocity[1] = 3
                else:
                    self.velocity[1] = -3
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            self.frameTimer = 2
        else:
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            self.frameTimer -= 1
        
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
        self.exclamation,temp = load_image('exclamationMark.png', -1)

    def update(self):
        if self.state is "standing":
            if self.facingRight:
                self.switchTimer += 1
                if self.switchTimer == 35:
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
        elif self.state is "surprised":
            self.frameTimer -= 1
            if self.frameTimer <= 0:
                self.state = "running"
                self.frameTimer = 50
                self.facingRight = True
                self.image = pygame.transform.flip(self.image,True,False)

    def runAway(self):
        if self.state is not "surprised":                
            self.state = "surprised"
            self.frameTimer = 20

class leatherFaceObject(pygame.sprite.Sprite):
    def __init__(self,image, position, hideBox, hidingType):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image, -1)
        self.rect.topleft = position
        self.hideBox = pygame.Rect(hideBox)
        self.hideSurface = pygame.Surface((self.hideBox.w,self.hideBox.h))
        self.hideSurface.convert()
        self.hideSurface.fill((0,0,0))
        self.hideSurface.set_alpha(50)
        self.hidingType = hidingType

    def checkHidingSpot(self,state,hitBox):
        if self.hideBox.colliderect(hitBox) and state == self.hidingType:
            return True
        else:
            return False

class leatherFaceExclamationMark(pygame.sprite.Sprite):
    def __init__(self,position):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('exclamationMark.png', -1)
        self.rect.topleft = (position[0] - 50, position[1] - 30)
        self.frameCounter = 50

    def update(self):
        self.frameCounter -= 1
        if self.frameCounter <= 0:
            self.kill()

class pinkSpiderPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('pinkSpider.png', -1)
        self.originalImage = None
        self.rightWingStrength = 5
        self.leftWingStrength = 5
        self.velocity = [0,0]
        self.opacity = 0
        self.rect.x = 600
        self.rect.y = 1700
        self.state = "grounded"

    def update(self):
        keys = pygame.key.get_pressed()
        if self.state == "grounded":
            self.opacity += 2
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
            self.image.set_alpha(255 - (self.opacity / 10))
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
            if self.opacity > 0:
                self.velocity[1] -= self.opacity
                self.opacity -= 4
            balance = self.velocity[2] - self.velocity[3]
            self.image = pygame.transform.rotate(self.originalImage, 5 * balance)
            self.velocity[0] = balance * 2
            
        self.rect.x += self.velocity[0]
        if self.rect.x < 500:
            self.rect.x = 500
        elif self.rect.x + self.rect.width > 1500:
            self.rect.x = 1500 - self.rect.width
        self.rect.y += self.velocity[1]
        if self.state == "grounded":
            if self.rect.y < 0:
                self.rect.y = 0
            elif self.rect.bottom > 1800:
                self.rect.bottom = 1800

    def transform(self):
        self.image, temp = load_image("pinkSpiderWings.png", -1)
        self.originalImage = self.image
        self.state = "flying"
        self.velocity = [self.velocity[0],self.velocity[1], 0, 0]
        self.opacity = 80

class pinkSpiderFly(pygame.sprite.Sprite):
    def __init__(self, bugType):
        pygame.sprite.Sprite.__init__(self)
        if bugType is "fly":                
            self.image, self.rect = load_image('fly.png', -1)
        else:
            self.image, self.rect = load_image('butterfly.png', -1)
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        self.rect.x = randint(600,1400)
        self.rect.y = randint(1200,1800)
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

class pinkSpiderBird(pygame.sprite.Sprite):
    def __init__(self,position,velocity,duration):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("pinkSpiderBirdAnimation.png", -1)
        if velocity[0] < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            self.images = [self.image.subsurface((0,0),(200,350)),self.image.subsurface((0,350),(200,350))]
        elif velocity[1] > 0:
            self.image = pygame.transform.rotate(self.image, -90)
            self.images = [self.image.subsurface((0,0),(350,200)),self.image.subsurface((350,0),(350,200))]
        elif velocity[1] < 0:
            self.image = pygame.transform.rotate(self.image, 90)
            self.images = [self.image.subsurface((0,0),(350,200)),self.image.subsurface((350,0),(350,200))]
        else:
            self.images = [self.image.subsurface((0,0),(200,350)),self.image.subsurface((0,350),(200,350))]
        self.animationFrame = 0
        self.image = self.images[self.animationFrame]
        self.rect.center = position
        self.life = duration
        self.velocity = velocity

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.life -= 1
        self.animationFrame = not self.animationFrame
        self.image = self.images[self.animationFrame]
        if self.life <= 0:
            self.kill()
            
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
        if self.sprite.rect.bottom > 6000:
            self.sprite.rect.bottom = 6000
        self.offset[0] += self.slope['x']
        self.offset[1] -= self.slope['y']
        if self.offset[1] < -3600:
            self.offset[1] = -3600
        elif self.offset[1] > 2200:
            self.offset[1] = 2200
        if self.offset[0] > 4400:
            self.offset[0] = 4400
        elif self.offset[0] < -5400:
            self.offset[0] = -5400
        self.trueWidth -= 0.05
        self.trueHeight -= 0.05
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
        self.rect.center = (randint(-4000,4000),randint(-2500,2200))
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
        self.speed = 0.01
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
            if self.frameTimer > 0:
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
                self.speed -= 2
                if self.fishNum <= 0:
                    return True
                else:
                    return False
        elif obstacle is "bear":
            if self.state is "submerged":
                return False
            else:
                
                self.fishNum -= 1
                self.speed -= 2
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
    def __init__(self,speed):
        pygame.sprite.Sprite.__init__(self)
        typeList = {0:"log",1:"bear",2:"log",3:"bear",4:"Tree",5:"Tree"}
        self.type = typeList[randint(0,5)]
        self.distance = 100
        self.scaleWidth = 0
        self.scaleHeight = 0
        if self.type == "log":
            self.image, self.rect = load_image("log.png", -1)
            self.rect.topleft = (470, 340)
            self.originalImage = self.image
        elif self.type == "bear":
            self.originalImage, self.rect = load_image("bear.png", -1)
            self.image = pygame.transform.scale(self.originalImage,(int(self.originalImage.get_width() * 0.2),int(self.originalImage.get_height() * 0.2)))
            self.rect = self.image.get_rect()
            self.scaleWidth = (self.originalImage.get_width() - self.image.get_width()) / (self.distance/speed)
            self.scaleHeight = (self.originalImage.get_height() - self.image.get_height()) / (self.distance/speed)
            self.rect.topleft = (200, 230)
            self.interpolator = Interpolator((500,230),(-200,600),self.distance/speed/60,60)
        else:
            self.originalImage, self.rect = load_image("summerTree.png", -1)
            if randint(0,1):
                self.type = "leftTree"
                self.rect.topleft = (300, -100)
                self.interpolator = Interpolator((400,100),(-100,300),self.distance/speed/60,60)
            else:
                self.type = "rightTree"
                self.rect.topleft = (500,-100)
                self.interpolator = Interpolator((500,100),(1000,300),self.distance/speed/60,60)
                self.image = pygame.transform.flip(self.originalImage,True,False)

            self.image = pygame.transform.scale(self.originalImage,(int(self.originalImage.get_width() * 0.2),int(self.originalImage.get_height() * 0.2)))
            self.rect = self.image.get_rect()
            self.scaleWidth = (self.originalImage.get_width() - self.image.get_width()) / (self.distance/speed)
            self.scaleHeight = (self.originalImage.get_height() - self.image.get_height()) / (self.distance/speed)
            

    def updateDistance(self, speed):
        self.distance -= speed
        self.rect.y += 2 * speed
        if self.distance <= 0:
            self.kill()
        
    def update(self):
        if self.type is "log":
            self.rect.centerx = 500
            scaleWidth = self.originalImage.get_width() - int(self.distance)
            scaleHeight = self.originalImage.get_height() - (int(self.distance) / 2)
            if scaleWidth < 0:
                scaleWidth = 1
            if scaleHeight < 0:
                scaleHeight = 1
            self.image = pygame.transform.scale(self.originalImage, (scaleWidth, scaleHeight))
        else:
            self.rect.width += self.scaleWidth
            math.ceil(self.rect.width)
            if self.rect.width > self.originalImage.get_width():
                self.rect.width = self.originalImage.get_width()
            self.rect.height += self.scaleHeight
            math.ceil(self.rect.height)
            if self.rect.height > self.originalImage.get_height():
                self.rect.height = self.originalImage.get_height()
            self.image = pygame.transform.scale(self.originalImage,(int(self.rect.w),int(self.rect.h)))
            self.rect.center = self.interpolator.pos
            nextPos = self.interpolator.next()
            if nextPos == None:
                self.kill()

class everFreePlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.originalImage, self.rect = load_image("breedingHide.png", -1)
        self.image = self.originalImage
        self.velocity = [False,True]
        self.slope = [0,5]
        self.touchingSurface = False
        self.unattachableTime = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_RIGHT]:
            self.velocity[0] = True
            self.image = pygame.transform.flip(self.originalImage,True,False)
        elif keys[K_LEFT]:
            self.velocity[0] = -1
            self.image = self.originalImage
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
        self.goal.image, self.goal.rect = load_image("carrot.png", -1)
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
        self.player.rect.bottom = 600 - self.columns[self.player.position].totalHeight()
        totalHeight = 0
        for i in self.columns:
            totalHeight += i.totalHeight()
        self.goal.rect.y = totalHeight /  5

    def draw(self,screen):
        for i in range(self.NUMCOLUMNS):
            self.columns[i].drawColumn(screen)
        if self.player.carrying:
            pygame.draw.rect(screen,(250,0,0),pygame.Rect(self.player.rect.left,self.player.rect.top - 100, 100, 100))
        if self.bugs:
            screen.blit(self.bugs.image, self.bugs.rect.topleft)
        screen.blit(self.goal.image, self.goal.rect.topleft)
        pygame.draw.line(screen,(250,250,250),(self.goal.rect.x + 53,0),(self.goal.rect.x + 53,self.goal.rect.y + 13))

    def allowMove(self,position, goingRight):
        if goingRight:
            if position < 8:
                if abs(self.columns[position].height - self.columns[position + 1].height) <= 1:
                    self.player.rect.bottom = 600 - self.columns[position +1].totalHeight()
                    return True
                else:
                    return False
            else:
                return False
        else:
            if position > 0:
                if abs(self.columns[position].height - self.columns[position -1].height) <= 1:
                    self.player.rect.bottom = 600 - self.columns[position -1].totalHeight()
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
        self.image = pygame.transform.flip(self.image,True,False)
        self.rect.x = 10
        self.rect.y = 500
        self.offset = 0
        self.footPrintTimer =  20
        self.jumpTimer = False

    def update(self):
        self.footPrintTimer -= 1
        if self.footPrintTimer < 0:
            self.footPrintTimer = 20
        if self.jumpTimer > 0:
            self.rect.y = 400
            self.jumpTimer -= 1
            if self.jumpTimer <= 0:
                self.rect.bottom = 600
                self.jumpTimer = -20
        else:
            keys = pygame.key.get_pressed()
            if self.jumpTimer < 0:
                self.jumpTimer += 1
            if keys[K_DOWN]:
                self.rect.y = 550
            elif keys[K_UP]:
                if self.jumpTimer == 0:
                    self.jumpTimer = 60
            else:
                self.rect.y = 500

    def draw(self,screen):
        screen.blit(self.image, (self.rect.x,self.rect.y))

class hurryGoRoundObstacle(pygame.sprite.Sprite):
    def __init__(self, time):
        pygame.sprite.Sprite.__init__(self)
        self.safeRect = None
        if time <= 25:
            self.image,self.rect = load_image("doubtFrog.png",-1)
            self.image = pygame.transform.rotate(self.image, -90)
            self.rect = self.image.get_rect()
            self.image = pygame.transform.scale(self.image,(self.rect.w,self.rect.h - 30))
            self.rect = self.image.get_rect()
            self.frameCounter = -1
        elif time > 25 and time <= 50:
            self.image, self.rect = load_image("leatherFaceTarget.png",-1)
            self.frameCounter = 30
            self.image = pygame.transform.flip(self.image, True,False)
        elif time > 50 and time <= 75:
            self.image, self.rect = load_image("turkey.png", -1)
            self.frameCounter = -1
        elif time > 75 and time <= 100:
            self.image, self.rect = load_image("snowman.png",-1)
            self.frameCounter = -1
            self.safeRect = pygame.Rect(1100,516,100,84)
        elif time > 100 and time <= 125:
            self.image, self.rect = load_image("rabbit.png",-1)
            self.frameCounter = 10
        else:
            self.image,self.rect = load_image("leatherFaceTarget.png",-1)
            self.frameCounter = 30
        self.speed = time / 3
        if self.speed < 5:
            self.speed = 5
        self.rect.x = 1100
        self.rect.bottom = 600
        if self.safeRect:
            self.rect.h = 116
            self.rect.y = 400

    def update(self):
        self.rect.x -= self.speed
        if self.safeRect:
            self.safeRect.x = self.rect.x
        if self.frameCounter > -1:
            self.frameCounter -= 1
            if self.frameCounter == 0:
                if self.rect.bottom == 600:
                    self.rect.bottom = 500
                else:
                    self.rect.bottom = 600
                self.frameCounter = 30

        if self.rect.right < 0:
            self.kill()

    def draw(self,screen):
        screen.blit(self.image,(self.rect.x,self.rect.y))

    def fallOver(self):
        self.image = pygame.transform.rotate(self.image, 90)
        self.safeRect = None
        self.rect.x -= 100

class hurryGoRoundFootprint(pygame.sprite.Sprite):
    def __init__(self,position,flipped):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("footPrint.png", -1)
        self.flowerImage, temp = load_image("flower.png",-1)
        self.image = pygame.transform.flip(self.image,False,flipped)
        self.rect.midbottom = position
        self.flowerSize = 0

    def draw(self,screen):
        self.flowerSize += 1
        self.rect.x -= 5
        screen.blit(self.image,(self.rect.x, self.rect.y))
        if self.flowerSize > 100:
            screen.blit(self.flowerImage.subsurface((0,0),(49,45 + (self.flowerSize / 4))),(self.rect.x,self.rect.bottom - (45 + (self.flowerSize/4))))
        if self.rect.right < 0:
            self.kill()

class hurryGoRoundTree(pygame.sprite.Sprite):
    def __init__(self,time,images):
        pygame.sprite.Sprite.__init__(self)
        if time <= 25:
            #self.image, self.rect = load_image("summerTree.png", -1)
            self.image = images[0]
        elif time <= 50:
            if randint(0,1):
                #self.image, self.rect = load_image("fallTree.png",-1)
                self.image = images[1]
            else:
                #self.image, self.rect = load_image("fallTreeRed.png",-1)
                self.image = images[2]
        elif time <= 75:
            #self.image, self.rect = load_image("bareTree.png",-1)
            self.image = images[3]
        elif time <= 100:
            #self.image, self.rect = load_image("snowyTree.png",-1)
            self.image = images[4]
        else:
            self.image = images[5]
        self.rect = self.image.get_rect()
        self.image = pygame.transform.flip(self.image, randint(0,1),False)
        self.rect.x = 1100

    def update(self):
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()

    def draw(self,screen):
        screen.blit(self.image,self.rect.topleft)

class pinkCloudAssemblyPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("pinkSpiderWings.png",-1)
        self.rect.center = (500,300)
        self.velocity = 0
        self.distance = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            self.velocity = 4
        elif keys[K_DOWN]:
            self.velocity = -4
        else:
            self.velocity = 0
        self.rect.y += self.velocity
        self.distance += self.velocity

class pinkCloudAssemblyStairs(pygame.sprite.Sprite):
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("stairwayToHeaven.png", -1)
        self.rect.topleft = pos

    def update(self):
        if self.rect.y > 1000:
            self.kill()

class pinkCloudAssemblyObject(pygame.sprite.Sprite):
    def __init__(self,image):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(image,-1)
        self.image = pygame.transform.rotate(self.image, randint(0,360))
        if randint(0,1):
            self.rect.x = randint(0,400)
        else:
            self.rect.x = randint(600,1000)
        self.rect.y = randint(1000,5000) * -1

    def update(self,movement):
        self.rect.y += movement

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

class cdHUD(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [1,1]
        self.images[0],self.rect = load_image("cdHUDPause.png")
        self.images[1], self.rect = load_image("cdHUD.png")
        self.image = self.images[0]
        self.whichImage= False
        self.rect.topleft = (0,600)
        self.trackDisplay = pygame.font.Font(None, 36)
        self.trackNumber = 1
        self.stopButton = pygame.Rect(405,605,42,40)
        self.backButton = pygame.Rect(467,610,28,29)
        self.playButton = pygame.Rect(518,609,26,31)
        self.forwardButton = pygame.Rect(565,613,32,23)

    def draw(self,screen):
        screen.blit(self.image,self.rect.topleft)
        screen.blit(self.trackDisplay.render(str(self.trackNumber), 1, (191,218,2)), (630,610))

    def interpretInput(self,pos):
        if self.stopButton.collidepoint(pos):
            return "STOP"
        elif self.backButton.collidepoint(pos):
            return "BACK"
        elif self.playButton.collidepoint(pos):
            self.whichImage = not self.whichImage
            self.image = self.images[self.whichImage]
            return "PLAY"
        elif self.forwardButton.collidepoint(pos):
            return "FORWARD"

def changeTrack(direction,gameData):
    gameData['spriteList'].empty()
    if direction is "BACK":
        if gameData['trackFrameCounter'] > 0:
            gameData['trackNumber'] -= 2
            gameData['trackFrameCounter'] = 50
        else:
            gameData['trackNumber'] -= 1
            gameData['trackFrameCounter'] = 50
        if gameData['trackNumber'] < 0:
            gameData['trackNumber'] = 10
    # Change track to Rocket Dive
    if gameData['trackNumber'] == 1:
        gameData['player'] = rocketDivePlayer()
        gameData['spriteList'].add(gameData['player'])
        gameData['missile'] = rocketDiveMissile((1000,300))
        gameData['distance'] = 1000
        gameData['frameCounter'] = 100
    # Change track to Leather Face
    if gameData['trackNumber'] == 2:
        newBackground = pygame.Surface((1500,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        pygame.draw.polygon(newBackground,(200,200,200),[(0,100),(1500,100),(1500,470),(0,470)])
        gameData['backGround'] = newBackground
        gameData['backGroundPos'] = 0
        gameData['player'] = leatherFacePlayer()
        gameData['target'] = leatherFaceTarget()
        gameData['leatherFaceDownstairsObjects'] = pygame.sprite.OrderedUpdates(leatherFaceObject('door.png',(400,220),(400,220,100,250),"standing"))
        gameData['leatherFaceDownstairsObjects'].add(leatherFaceObject('bookshelf.png',(800,170),(700,200,100,300),"standing"))
        gameData['leatherFaceDownstairsObjects'].add(leatherFaceObject('stairs.png',(1500,250),(0,0,0,0),"stairs"),gameData['player'],gameData['target'])
        gameData['leatherFaceUpstairsObjects'] = pygame.sprite.OrderedUpdates(leatherFaceObject('refridgerator.png',(1000,270),(900,300,100,200),"standing"))
        gameData['leatherFaceUpstairsObjects'].add(leatherFaceObject('table.png',(500,370),(500,400,300,100),"lyingDown"))
        gameData['leatherFaceUpstairsObjects'].add(leatherFaceObject('window.png',(1500,300),(0,0,0,0),"window"))
        gameData['leatherFaceUpstairsObjects'].add(gameData['player'],gameData['target'])
        gameData['leatherFaceObjects'] = pygame.sprite.OrderedUpdates(gameData['leatherFaceDownstairsObjects'],gameData['leatherFaceUpstairsObjects'])
        gameData['leatherFaceObjects'].remove(gameData['player'],gameData['target'])
        gameData['spriteList'].add(gameData['leatherFaceDownstairsObjects'])
        gameData['frameCounter'] = 0
    # Change track to Pink Spider
    elif gameData['trackNumber'] == 3:
        sideScrollingSurface = pygame.Surface((2000,1800))
        sideScrollingSurface = sideScrollingSurface.convert()
        sideScrollingSurface.fill((0,0,0))
        gameData['sideScrollingSurface'] = sideScrollingSurface
        gameData['stars'] = []
        for i in range(100):
            size = randint(10,25)
            temp = pygame.Surface((size,size))
            temp = temp.convert()
            temp.fill((250,250,250))
            position = (randint(0,2000),randint(0,1000))
            gameData['stars'].append((temp,position))
        gameData['player'] = pinkSpiderPlayer()
        gameData['spriteList'].add(gameData['player'],pinkSpiderBird((1000,1900),(0,-5),200))
        gameData['backGround'] = pygame.Surface((2000, 1800))
        gameData['backGround'] = gameData['backGround'].convert()
        gameData['backGround'].fill((0,0,0))
        webImage, temp = load_image('spiderweb.png')
        gameData['backGround'].blit(webImage,(500,1200))
        gameData['bouncingRect'] = pygame.Rect(500,1790,1000,10)
        gameData['bounces'] = 0
    # Change track to Doubt '97
    elif gameData['trackNumber'] == 4:
        gameData['player'] = doubtPlayer()
        for i in range(30):
            gameData['spriteList'].add(doubtEnemy())
        newBackground = pygame.Surface((10000,6130))
        newBackground = newBackground.convert()
        red = 67
        green = 233
        blue = 41
        for i in [0,600,1200,1800,2400,3000,3600,4200,4800,5400,6000]:
            newBackground.fill((red,green,blue),pygame.Rect(0,i,10000,600))
            red -= 5
            green -= 20
            blue -= 3
        gravelImg, temp = load_image("gravel.png", -1)
        rotation = [0,90,180,270]
        for i in range(100):
            gravelImg = pygame.transform.rotate(gravelImg, choice(rotation))
            newBackground.blit(gravelImg, (i * 100, 6000))
        tankCorner, temp = load_image("tankCorner.png", -1)
        tankPipe, temp = load_image("tankFrame.png")
        for i in range(100):
            newBackground.blit(tankPipe,(i*100,0))
            newBackground.blit(tankPipe,(i*100,6100))
        tankPipe = pygame.transform.rotate(tankPipe,90)
        for i in range(61):
            newBackground.blit(tankPipe,(0,i * 100))
            newBackground.blit(tankPipe,(9970,i * 100))
        newBackground.blit(tankCorner,(9940,6070))
        newBackground.blit(pygame.transform.flip(tankCorner,True,False),(0,6070))
        newBackground.blit(pygame.transform.flip(tankCorner,True,True),(0,0))
        newBackground.blit(pygame.transform.flip(tankCorner,False,True),(9940,0))
        gameData['backGround'] = newBackground
        gameData['frameCounter'] = 0
    # Change track to Fish Scratch Fever    
    elif gameData['trackNumber'] == 5: 
        newBackground = pygame.Surface((1000,600))
        newBackground = newBackground.convert()
        newBackground.fill((0,0,0))
        pygame.draw.polygon(newBackground,(20,40,200),[(0,600),(470,340),(530,340),(1000,600)])
        gameData['backGround'] = newBackground
        gameData['player'] = fishScratchFeverPlayer()
        gameData['frameCounter'] = 130
        gameData['targetDistance'] = 3000
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
        gameData['goal'] = pygame.sprite.Sprite()
        gameData['goal'].image,gameData['goal'].rect = load_image('wings.png',-1)
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
        gameData['spriteList'].add(gameData['player'],hurryGoRoundObstacle(0.0))
        gameData['flipped'] = False
        gameData['frameCounter'] = 100
        gameData['seasonCounter'] = 0.0
        gameData['treeImages'] = [0,0,0,0,0,0]
        gameData['treeImages'][0],temp = load_image("summerTree.png",-1)
        gameData['treeImages'][1],temp = load_image("fallTree.png",-1)
        gameData['treeImages'][2],temp = load_image("fallTreeRed.png",-1)
        gameData['treeImages'][3],temp = load_image("bareTree.png",-1)
        gameData['treeImages'][4],temp = load_image("snowyTree.png",-1)
        gameData['treeImages'][5],temp = load_image("springTree.png",-1)
    # Change Track to Pink Cloud Assembly
    elif gameData['trackNumber'] == 9:
        gameData['player'] = pinkCloudAssemblyPlayer()
        gameData['stairCaseList'] = pygame.sprite.Group(pinkCloudAssemblyStairs((500,500)),pinkCloudAssemblyStairs((500,300)),pinkCloudAssemblyStairs((500,100)))
        gameData['stairCaseList'] = pygame.sprite.Group(pinkCloudAssemblyStairs((500,-100)))
        gameData['spriteList'].add(gameData['player'], pinkCloudAssemblyObject('fly.png'), pinkCloudAssemblyObject('bear.png'),pinkCloudAssemblyObject('hideLeatherFace.png'))
        gameData['spriteList'].add(pinkCloudAssemblyObject('salmon.png'),pinkCloudAssemblyObject('tadpole.png'),pinkCloudAssemblyObject('butterfly.png'))
    # Set game back to beginning
    elif gameData['trackNumber'] == 10:
        gameData['trackNumber'] = 0
        gameData['grid'] = spreadBeaverGrid()
    gameData['trackNumber'] += 1
        

def main():
    
    #Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((1000, 650))
    pygame.display.set_caption('Pink Cloud Assembly Language')
    pygame.mouse.set_visible(1)

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
    theCDHUD = cdHUD()
    paused = False
    pauseTimer = -1
    endMessage = "You Win!"
    frameTimer = 30
    speed = 5
    trackNumber = 1
    allsprites = pygame.sprite.OrderedUpdates()
    gameData = {'grid': spreadBeaverGrid(),'player': None,'trackNumber':trackNumber,'spriteList':allsprites,'background':background, 'trackFrameCounter':0}
    distanceTracker = pygame.font.Font(None, 36)
    
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
            elif event.type == MOUSEBUTTONDOWN:
                response = theCDHUD.interpretInput(event.pos)
                if response is "STOP":
                    pygame.quit()
                elif response is "BACK":
                    allsprites.empty()
                    changeTrack("BACK",gameData)
                elif response is "PLAY":
                    paused = not paused
                elif response is "FORWARD":
                    allsprites.empty()
                    changeTrack("FORWARD",gameData)
        if not paused:
            screen.blit(background, (0,0))
            # ----- Track 1, Spread Beaver -----
            if gameData['trackNumber'] == 1:
                gameData['grid'].update()
                gameData['grid'].draw(screen)
                if gameData['grid'].deadOnTheWater():
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "You got stuck :("
                    if pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
                if gameData['grid'].pos == gameData['grid'].goalPos:
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "Lets get started"
                    if pauseTimer == 0:
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
                gameData['missile'].update(gameData['player'].rect.center)
                screen.blit(gameData['missile'].image,gameData['missile'].rect.topleft)
                if gameData['missile'].rect.colliderect(gameData['player'].rect):                        
                    if pauseTimer == -1:                
                        pauseTimer = 40
                        paused = True
                        endMessage = "Owned :("
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
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
                screen.blit(gameData['backGround'], (gameData['backGroundPos'],0))
                for i in gameData['spriteList'].sprites():
                    if gameData['frameCounter'] == 0:
                        if type(i) == leatherFaceObject:
                            i.rect.x += -1 * gameData['player'].velocity
                            i.hideBox.x += -1 * gameData['player'].velocity
                            if i.hidingType is "stairs":
                                gameData['backGroundPos'] = i.rect.right - 1500
                                if gameData['backGroundPos'] > 0:
                                    gameData['backGroundPos'] = 0
                                if i.rect.colliderect(gameData['player'].rect):
                                    if gameData['spriteList'] is gameData['leatherFaceDownstairsObjects']:
                                        gameData['spriteList'] = gameData['leatherFaceUpstairsObjects']
                                        gameData['spriteList'].add(gameData['target'])
                                        gameData['player'].rect.x -= 100
                                        gameData['frameCounter'] = 50
                                        gameData['backGroundPos'] = 0
                                    else:
                                        gameData['spriteList'] = gameData['leatherFaceDownstairsObjects']
                                elif i.rect.colliderect(gameData['target'].rect):
                                    gameData['target'].kill()
                                    gameData['target'].rect.x += 100
                            elif i.hidingType is "window":
                                if i.rect.x < gameData['target'].rect.right:
                                    changeTrack("FORWARD", gameData)
                                    frameTimer = 50
                                    gameData['frameCounter'] = 90
                                    break
                            else:
                                screen.blit(i.hideSurface,i.hideBox.topleft)
                        elif type(i) == leatherFaceTarget:
                            if i.rect.colliderect(gameData['player'].rect):
                                if pauseTimer == -1:
                                    pauseTimer = 40
                                    paused = True
                                    endMessage = "You win!"
                                    break
                                elif pauseTimer == 0:
                                    changeTrack("FORWARD",gameData)
                                    frameTimer = 50
                                    gameData['frameCounter'] = 90
                                    break
                            i.rect.x += -1 * gameData['player'].velocity
                            if not i.facingRight:
                                if not gameData['player'].hiding:
                                    gameData['frameCounter'] = 90
                                    i.runAway()
                                    gameData['spriteList'].add(leatherFaceExclamationMark(gameData['target'].rect.topleft))
                                    frameTimer = 40
                                    #break
                                else:
                                    visible = True
                                    for j in gameData['leatherFaceObjects']:
                                        if j.checkHidingSpot(gameData['player'].hidingPosture(),gameData['player'].rect):
                                            visible = False
                                            break
                                    if visible:
                                        i.runAway()
                                        gameData['frameCounter'] = 90
                                        gameData['spriteList'].add(leatherFaceExclamationMark(gameData['target'].rect.topleft))
                                        frameTimer = 40
                                        #break
                    else:
                        i.rect.x -= 3
                        if type(i) == leatherFaceObject:
                            i.hideBox.x -= 3
                            screen.blit(i.hideSurface,i.hideBox.topleft)
                if gameData['target'].rect.colliderect(gameData['player'].rect):
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "You win!"
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
                        frameTimer = 50
                if gameData['frameCounter'] > 0:
                    gameData['frameCounter'] -= 1
            # ----- Track 4, Pink Spider -------
            elif gameData['trackNumber'] == 4:
                allsprites = pygame.sprite.Group()
                gameData['sideScrollingSurface'].blit(gameData['backGround'], (0,0))
                frameTimer -= 1
                if frameTimer == 0:
                    if randint(0,5) <= 1:
                        gameData['spriteList'].add(pinkSpiderFly("butterfly"))
                    else:
                        gameData['spriteList'].add(pinkSpiderFly("fly"))
                    frameTimer = 200 + randint(0,200)
                for i in gameData['spriteList'].sprites():
                    if type(i) != pinkSpiderPlayer and gameData['player'].state is "grounded" and type(i) != pinkSpiderBird and gameData['player'].rect.colliderect(i.rect):
                        if i.bugType is not "fly":
                            gameData['player'].transform()
                            gameData['spriteList'].remove(gameData['player'])
                            gameData['spriteList'].add(pinkSpiderBird((400,700),(3,0),300))
                        else:
                            if gameData['player'].opacity > 300:
                                i.kill()
                                gameData['player'].opacity -= 300
                            else:
                                i.getCaught()
                
                for i in gameData['stars']:
                    gameData['sideScrollingSurface'].blit(i[0],i[1])
                gameData['spriteList'].update()
                gameData['spriteList'].draw(gameData['sideScrollingSurface'])
                sideScrollingOffset = gameData['player'].velocity
                if gameData['player'].state == "grounded":
                    screen.blit(gameData['sideScrollingSurface'], (-500,-1200))
                    if gameData['player'].opacity >= 2500:
                        if pauseTimer == -1:
                            pauseTimer = 40
                            paused = True
                            endMessage = "You Faded Away :("
                        elif pauseTimer == 0:
                            changeTrack("FORWARD",gameData)
                else:
                    if gameData['player'].rect.colliderect(gameData['bouncingRect']) and gameData['bounces'] < 3:
                        gameData['player'].leftWingStrength = 6
                        gameData['player'].rightWingStrength = 6
                        gameData['player'].rect.bottom = gameData['bouncingRect'].y - 1
                        gameData['bounces'] += 1
                    gameData['player'].update()
                    screen.blit(gameData['sideScrollingSurface'], (500 - gameData['player'].rect.x,300 - gameData['player'].rect.y))
                    screen.blit(gameData['player'].image, (500,300))
                    if gameData['player'].rect.y > 1800:
                        if pauseTimer == -1:
                            pauseTimer = 40
                            paused = True
                            endMessage = "You couldn't fly"
                        elif pauseTimer == 0:
                            changeTrack("FORWARD",gameData)
            # ----- Track 5, Doubt '97 -----
            elif gameData['trackNumber'] == 5:
                allsprites = pygame.sprite.Group()
                gameData['frameCounter'] += 1
                if gameData['frameCounter'] >= 300:
                    gameData['spriteList'].add(doubtEnemy())
                    gameData['frameCounter'] = 0
                gameData['spriteList'].update()
                gameData['player'].update()
                offset = gameData['player'].offset
                screen.blit(gameData['backGround'], (-5000 - offset[0],-2000 + offset[1]))
                screen.blit(gameData['player'].sprite.image, (500,300))
                for i in gameData['spriteList'].sprites():
                    screen.blit(i.image, (i.rect.x - offset[0], i.rect.y + offset[1]))
                    if pygame.Rect(i.rect.x - offset[0],i.rect.y + offset[1], i.rect.w,i.rect.h).colliderect(pygame.Rect(500,300,gameData['player'].trueWidth,gameData['player'].trueHeight)):
                        i.kill()
                        gameData['player'].eat()
                if gameData['player'].sprite.rect.width < 5:
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "So hungry"
                    elif pauseTimer == 0:
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
                            if pauseTimer == -1:
                                pauseTimer = 40
                                paused = True
                                endMessage = "You didn't make it home"
                            elif pauseTimer == 0:
                                changeTrack("FORWARD",gameData)
                gameData['frameCounter'] -= 1
                gameData['targetDistance'] -= curSpeed
                if gameData['frameCounter'] == 0 and gameData['targetDistance'] > 0:
                    gameData['spriteList'].add(fishScratchFeverObstacle(curSpeed))
                    gameData['frameCounter'] = 130
                if gameData['targetDistance'] <= 0:
                    gameData['player'].beFree()
                    if gameData['player'].frameTimer <= 0:
                        if pauseTimer == -1:
                            pauseTimer = 40
                            paused = True
                            endMessage = "Made it Home"
                        elif pauseTimer == 0:
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
                    gameData['goal'].rect.y -= 5
                    gameData['player'].rect.center = gameData['goal'].rect.center
                    gameData['player'].velocity[1] = -1
                    gameData['player'].slope[1] = 5
                    if gameData['goal'].rect.top <= 0:                            
                        if pauseTimer == -1:
                            pauseTimer = 40
                            paused = True
                            endMessage = "Ever Free"
                        elif pauseTimer == 0:
                            changeTrack("FORWARD",gameData)
                if gameData['player'].rect.colliderect(gameData['lava'].rect):
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "Never Free"
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
                gameData['sideScrollingSurface'].blit(gameData['lava'].image, (gameData['lava'].rect.x,gameData['lava'].rect.y))
                gameData['sideScrollingSurface'].blit(gameData['goal'].image,gameData['goal'].rect.topleft)
                screen.blit(gameData['sideScrollingSurface'], (500 - gameData['player'].rect.x,300 - gameData['player'].rect.y))
                screen.blit(gameData['player'].image, (500,300))
            # ----- Track 8, Breeding ------
            elif gameData['trackNumber'] == 8:
                screen.blit(gameData['background'], (0,0))
                gameData['grid'].update()
                gameData['grid'].draw(screen)
                if gameData['grid'].player.rect.colliderect(gameData['grid'].goal.rect):
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "You win"
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
                elif gameData['grid'].goal.rect.y * 5 < 600 - gameData['grid'].goal.rect.y:
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "You'll never make it now"
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
            # ----- Track 9 Hurry Go Round -----
            elif gameData['trackNumber'] == 9:
                allsprites = pygame.sprite.Group()
                screen.blit(gameData['background'], (0,0))
                treeKa = randint(0,100)
                if treeKa < 1:
                    gameData['spriteList'].add(hurryGoRoundTree(gameData['seasonCounter'],gameData['treeImages']))
                gameData['frameCounter'] -= 1
                if gameData['frameCounter'] <= 0:
                    gameData['spriteList'].add(hurryGoRoundObstacle(gameData['seasonCounter']))
                    gameData['frameCounter'] = randint(100,300)
                if gameData['player'].footPrintTimer == 0:
                    gameData['spriteList'].add(hurryGoRoundFootprint((gameData['player'].rect.x,600),gameData['flipped']))
                    gameData['flipped'] = not gameData['flipped']
                    gameData['player'].footPrintTimer = 20
                    gameData['seasonCounter'] += 0.3
                    if gameData['seasonCounter'] > 125:
                        if pauseTimer == -1:
                            pauseTimer = 40
                            paused = True
                            endMessage = "You made it!"
                        elif pauseTimer == 0:
                            changeTrack("FORWARD",gameData)
                gameData['spriteList'].update()
                for i in gameData['spriteList'].sprites():
                    if type(i) is hurryGoRoundPlayer:
                        i.draw(screen)
                    else:
                        if type(i) is hurryGoRoundObstacle:
                            if gameData['player'].rect.colliderect(i.rect):
                                gameData['player'].offset += 10
                                gameData['player'].rect.x += gameData['player'].offset
                                i.kill()
                            elif i.safeRect:
                                if gameData['player'].rect.colliderect(i.safeRect):
                                    i.fallOver()
                        i.draw(screen)
                if gameData['player'].rect.x >= 1000:
                    if pauseTimer == -1:
                        pauseTimer = 40
                        paused = True
                        endMessage = "See you in the Spring"
                    elif pauseTimer == 0:
                        changeTrack("FORWARD",gameData)
            # ----- Track 10 Pink Cloud Assembly -----
            elif gameData['trackNumber'] == 10:
                allsprites = pygame.sprite.Group()
                screen.blit(gameData['background'], (0,0))
                gameData['player'].update()
                if gameData['player'].distance > 1000000:
                    changeTrack("FORWARD",gameData)
                aboveScreen = False
                belowScreen = False
                for i in gameData['stairCaseList'].sprites():
                    i.rect.y += gameData['player'].velocity
                    if i.rect.y < 0:
                        aboveScreen = True
                    if i.rect.bottom > 600:
                        belowScreen = True
                    screen.blit(i.image, i.rect.topleft)
                if not aboveScreen:
                    gameData['stairCaseList'].add(pinkCloudAssemblyStairs((500,-199)))
                if not belowScreen:
                    gameData['stairCaseList'].add(pinkCloudAssemblyStairs((500,600)))
                for i in gameData['spriteList'].sprites():
                    if type(i) is pinkCloudAssemblyObject:
                        i.update(gameData['player'].velocity)
                        screen.blit(i.image,i.rect.topleft)
                screen.blit(gameData['player'].image,(500,300))
            allsprites.update()
            allsprites.draw(screen)
        gameData['trackFrameCounter'] -= 1
        if pauseTimer > 0:
            pauseTimer -= 1
            if pauseTimer == 0:
                paused = False
            screen.blit(distanceTracker.render(endMessage, 1, (200,10,0)),(500,300))
        elif pauseTimer == 0:
            pauseTimer = -1
            
        theCDHUD.trackNumber = gameData['trackNumber']
        theCDHUD.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()
