# ======================================================================================================================
#
# Andy Yang
# 24-06-21 (dd-mm-yy)
#
# Description:
# A basic platformer game, a custom level can be made using the attached map editor. 4 levels are preloaded and made,
# all sounds can be toggled on or off in the settings menu. The controls are the standard 'a' or left arrow to move
# left, 'd' or right arrow to move right, and space to jump. Space can be held to glide and slow the player's descent,
# and shift can be held while jumping to jump with less height. The player starts with 5 health points and will take 1
# point of damage upon collision with any damaging blocks. Coins are also placed throughout the map as collectibles,
# which will increase the score of the level.Please ensure all files are located in the right folders before the
# program is initiated. For a file directory, please refer to the 'fileList.txt' file in the game folder.
#
#
#
#
# *Comments refer to the code below them*
#
# ======================================================================================================================
# Notes
#
# - When a player is being squished by a moving platform and a stationary block, the collision of
# the platform takes priority and the player is able to pass through the moving platform. This keeps the player from
# getting stuck between a block and a moving platform. There are some levels which require the player to make use of
# this mechanic to complete. By standing right under a vertically moving platform and jumping when the platform comes
# into collision with the top of the player, the player is able to jump through the platform and land atop of it.
#
# - Most of the code in the main game section can be moved into the player class, and would probably be a little cleaner
# if written that way, but by the time I thought of it it was already kind of too late though so it's been left in the
# main program.
#
# - Cheats can be enabled in the variables section to stop the player from taking damage, and flight can be enabled for
# easier maneuverability around levels while testing.
#
# Known Bugs
#
# - Sometimes player is able to phase through bottom of vertically moving blocks, doesn't really affect gameplay and
# is not very noticeable, also very difficult to reproduce as of current testing, seems to be caused by some timing
# mismatch with the block movement and horizontal collision where the player triggers horizontal collision and skips
# vertical collision check? Upon further testing, this seems to be triggered when the player switches from freefalling
# to gliding just before contacting the top of a vertically moving block. Still not really sure why, but seems to be an
# issue with the initial colliderect collision check failing to activate.
#
# ======================================================================================================================


# Import necessary modules and initialization
import pygame
import sys
import random

pygame.init()

# File check: Ensures all files needed to run are accessible, if the files cannot be found, alerts the user as to which
# files are missing
# ----------------------------------------------------------------------------------------------------------------------
missingFileList = []
try:
    with open('platformer_assets/fileList.txt', 'r') as fileList:
        filesChecklist = fileList.readlines()
        for file in filesChecklist:
            try:
                with open(file.strip('\n'), 'r'):
                    pass
            except FileNotFoundError:
                missingFileList.append(file.replace("platformer_assets/", ""))
                missingFiles = "\n    ".join(missingFileList)
except FileNotFoundError:
    missingFileList.append('platformer_assets/fileList.txt')
    missingFiles = 'platformer_assets/fileList.txt'
if len(missingFileList) > 0:
    print(
        f"The game could not be initialized.\nFiles missing:\n    {missingFiles}\nPlease make sure the missing files "
        f"are placed within their respective folders in the 'platformer_assets' folder inside the game directory.")
    sys.exit()


# Functions ------------------------------------------------------------------------------------------------------------

# Attempts to convert a value to an integer, if it cannot be converted, returns 0
def intCheck(value):
    try:
        value = int(value)
    except ValueError or TypeError:
        return 0
    else:
        return value


# Displays FPS
def displayFPS(surface, location, font, color, FPScap):
    fps = font.render(f"FPS: {int(clock.get_fps())}", False, color)
    surface.blit(fps, location)
    pygame.display.update()
    clock.tick(FPScap)


# Import levels --------------------------------------------------------------------------------------------------------
maxLvls = 4
levels = []

for level in range(maxLvls):
    data = [[], 0]
    lvlData = open(f'platformer_assets//levels/level{level}_data.txt', 'r').readlines()
    for row in lvlData:
        rowData = []
        row = row.strip('\n').split(', ')
        for block in row:
            rowData.append(intCheck(block))
        data[0].append(rowData)
    levels.append(data)
levels[0][1] = 1


# Debugging functions --------------------------------------------------------------------------------------------------

# Draws grid lines onto display
def drawGrid(pos):
    for line in range(1, tileCount + 1):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tileSize), (width, line * tileSize))
    for line in range(0, tileCount * 4 + 1):
        pygame.draw.line(screen, (255, 255, 255), (line * tileSize - pos, 0),
                         (line * tileSize - pos, height))


# Classes --------------------------------------------------------------------------------------------------------------

# World class, takes world data and creates a list of the blocks and locations
class World:
    def __init__(self, data):
        self.blockList = []
        # Tracks current camera location compared to blocks
        self.cameraPos = 0
        # Score tracker and coin image
        self.score = 0
        self.scoreImage = pygame.transform.scale(pygame.image.load('platformer_assets/img/coin1.png'), (45, 45))
        # Sprite groups
        self.objects = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.finishFlags = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.damage = pygame.sprite.Group()
        self.movingBlocks = pygame.sprite.Group()
        # Reads list provided by data and converts it into locations for block placement
        currentRow = 0
        for row in data:
            column = 0
            for tile in row:
                # Dirt block
                if tile == 1:
                    self.image = pygame.image.load('platformer_assets/img/dirt.png')
                    block = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(block)
                    self.objects.add(block)
                # Assortment of grass blocks
                elif tile == 2:
                    self.image = pygame.image.load('platformer_assets/img/grass_left.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                elif tile == 3:
                    self.image = pygame.image.load('platformer_assets/img/grass_center.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                elif tile == 4:
                    self.image = pygame.image.load('platformer_assets/img/grass_right.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                elif tile == 5:
                    self.image = pygame.image.load('platformer_assets/img/grass_plat_left.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                elif tile == 6:
                    self.image = pygame.image.load('platformer_assets/img/grass_plat_center.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                elif tile == 7:
                    self.image = pygame.image.load('platformer_assets/img/grass_plat_right.png')
                    grassblock = Block(column * tileSize - self.cameraPos, currentRow * tileSize, self.image)
                    self.blocks.add(grassblock)
                    self.objects.add(grassblock)
                # Moving blocks, vertical and horizontal variants
                elif tile == 8:
                    movingBlock = MovingBlock(column * tileSize - self.cameraPos, currentRow * tileSize + 1, 0)
                    self.movingBlocks.add(movingBlock)
                    self.objects.add(movingBlock)
                elif tile == 9:
                    movingBlock = MovingBlock(column * tileSize - self.cameraPos, currentRow * tileSize + 1, 1)
                    self.movingBlocks.add(movingBlock)
                    self.objects.add(movingBlock)
                # Spike balls
                elif tile == 10:
                    ball = SpikeBall(column * tileSize + 2 - self.cameraPos, currentRow * tileSize + 13)
                    self.balls.add(ball)
                    self.damage.add(ball)
                    self.objects.add(ball)
                # Spikes, top facing and bottom facing
                elif tile == 11:
                    spikeTop = Spike(column * tileSize + 2 - self.cameraPos, currentRow * tileSize + tileSize / 2, 0)
                    self.spikes.add(spikeTop)
                    self.damage.add(spikeTop)
                    self.objects.add(spikeTop)
                elif tile == 12:
                    spikeBottom = Spike(column * tileSize + 2 - self.cameraPos, currentRow * tileSize, 1)
                    self.spikes.add(spikeBottom)
                    self.damage.add(spikeBottom)
                    self.objects.add(spikeBottom)
                # Coin
                elif tile == 13:
                    coin = Coin(column * tileSize - self.cameraPos, currentRow * tileSize)
                    self.coins.add(coin)
                    self.objects.add(coin)
                # Finish flag
                elif tile == 14:
                    finishFlag = Finish(column * tileSize - self.cameraPos,
                                        currentRow * tileSize - tileSize // 2 + 5)
                    self.finishFlags.add(finishFlag)
                    self.objects.add(finishFlag)
                column += 1
            currentRow += 1

    # Draws level onto screen
    def drawLvl(self):
        world.objects.draw(screen)
        world.balls.draw(mobLayer)
        world.coins.draw(mobLayer)
        menuLayer.blit(self.scoreImage, (5, 10))
        menuLayer.blit(smallFont.render(f'x {self.score}', True, (255, 204, 0)), (60, 20))
        # Draws rect / hitbox of each object if in debug mode
        if debug:
            for obj in world.objects:
                pygame.draw.rect(mobLayer, (255, 255, 255), obj.rect, 2)


# Spike Ball
class SpikeBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for img in range(1, 3):
            img = pygame.image.load(f'platformer_assets/img/spikeBall{img}.png')
            img = pygame.transform.scale(img, (tileSize, tileSize))
            self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.counter = 0
        self.width = self.image.get_rect().width
        self.height = self.image.get_rect().height

    # Moves one block left and one block right from starting position
    def update(self):
        self.rect.x += self.direction
        self.counter += 1
        if self.counter == 50:
            self.direction *= -1
            self.counter *= -1
        if self.counter % 10 == 0:
            if self.image == self.images[0]:
                self.image = self.images[1]
            else:
                self.image = self.images[0]


# Spike
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.image.load('platformer_assets/img/spike.png')
        if direction == 0:
            self.image = pygame.transform.rotate(self.image, 180)
        self.image = pygame.transform.scale(self.image, (tileSize, int(tileSize / 2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Button, creates a button with centered text
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text, size, font):
        super().__init__()
        self.defaultImage = pygame.image.load('platformer_assets/buttons/btndefault.png')
        self.defaultImage = pygame.transform.scale(self.defaultImage, size)
        self.hoverImage = pygame.image.load('platformer_assets/buttons/btnhover.png')
        self.hoverImage = pygame.transform.scale(self.hoverImage, size)
        self.pressedImage = pygame.image.load('platformer_assets/buttons/btnpressed.png')
        self.pressedImage = pygame.transform.scale(self.pressedImage, size)
        self.image = self.defaultImage
        self.text = font.render(text, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.textSize = font.size(text)
        self.textPos = (self.rect.centerx - (self.textSize[0] // 2), self.rect.centery - (self.textSize[1] // 2))
        self.clickCd = False
        self.coolDownCounter = 0
        buttons.add(self)

    # Returns True if the button is pressed
    def isPressed(self, mouseDown):
        mPos = pygame.mouse.get_pos()
        menuLayer.blit(self.image, self.rect)
        menuLayer.blit(self.text, self.textPos)
        # If button is on cooldown, starts cooldown timer and disables actions on the button until cooldown ends
        if self.clickCd:
            if self.coolDownCounter == FPS / 6:
                return True
            # Plays click sound if button is clicked
            elif self.coolDownCounter == 1 and sound:
                buttonClick.play()
        # If the button is visible and is clicked, returns True, changes image and puts button on cooldown
        elif self.rect.collidepoint(mPos):
            if mouseDown:
                self.image = self.pressedImage
                self.clickCd = True
            # If button is hovered but not clicked, changes image
            elif self.image != self.hoverImage:
                self.image = self.hoverImage
        # If button is neither hovered nor clicked, sets image to default
        elif self.image != self.defaultImage:
            self.image = self.defaultImage

    # Update function, basically the cooldown timer for the buttons
    def update(self):
        if self.clickCd:
            self.coolDownCounter += 1
            if self.coolDownCounter == FPS / 2:
                self.clickCd = False
                self.coolDownCounter = 0


# Toggle Button, draws a checkbox button and text to the left
class toggleButton(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        super().__init__()
        self.unpressedImage = pygame.image.load('platformer_assets/buttons/toggleunpressed.png')
        self.pressedImage = pygame.image.load('platformer_assets/buttons/togglepressed.png')
        self.pressed = True
        self.image = self.pressedImage
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.text = buttonFont.render(text, True, (255, 255, 255))
        self.textSize = buttonFont.size(text)
        self.textPos = (self.rect.x - 500, self.rect.centery - self.textSize[1] // 2)

    # Returns True as long as button is checkmarked
    def isPressed(self, mouseDown):
        mPos = pygame.mouse.get_pos()
        menuLayer.blit(self.image, self.rect)
        menuLayer.blit(self.text, self.textPos)
        # If button is pressed, changes state. Eg. if button is checked, unchecks it and vice versa
        if self.rect.collidepoint(mPos) and mouseDown:
            if self.pressed:
                self.image = self.unpressedImage
                self.pressed = False
            # If button is not clicked, sets image to default
            elif not self.pressed:
                self.image = self.pressedImage
                self.pressed = True
        return self.pressed


# Finish flag
class Finish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('platformer_assets/img/finish.png')
        self.image = pygame.transform.scale(self.image, (tileSize, int(tileSize * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Block
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (tileSize, tileSize))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Coin
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for img in range(1, 7):
            coinImg = pygame.image.load(f'platformer_assets/img/coin{img}.png')
            self.images.append(coinImg)
        self.image = self.images[0]
        self.counter = 0
        self.index = 0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # Update function for coins, basically times the animation for the coins rotating
    def update(self):
        mobLayer.blit(self.image, self.rect)
        self.counter += 1
        if self.counter >= FPS // 8:
            self.counter = 0
            self.index += 1
            if self.index > 5:
                self.index = 0
            self.image = self.images[self.index]


# Moving Block
class MovingBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, axis):
        super().__init__()
        self.image = pygame.image.load('platformer_assets/img/movingBlock.png')
        self.image = pygame.transform.scale(self.image, (tileSize, tileSize))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.height = tileSize // 2
        self.counter = 0
        self.direction = 1
        self.axis = axis

    # Update function for the moving blocks, basically handle the movement
    def update(self):
        if self.axis == 0:
            self.rect.x += self.direction
        elif self.axis == 1:
            self.rect.y += self.direction
        self.counter += 1
        if self.counter > tileSize:
            self.direction *= -1
            self.counter *= -1


# PLayer class, stores player images, wings images, and location
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.damageCD = 0
        self.health = 5
        self.heart = pygame.image.load('platformer_assets/img/heart.png')
        self.ghost = pygame.image.load('platformer_assets/img/ghost.png')
        self.ghost = pygame.transform.scale(self.ghost, (tileSize, tileSize))
        # Image and animation images
        self.rightImg = []
        self.leftImg = []
        # Loads player images facing left and right
        for num in range(1, 6):
            img_right = pygame.image.load(f'platformer_assets/img/player{num}.png')
            img_right = pygame.transform.scale(img_right, (60, 90))
            img_left = pygame.transform.flip(img_right, True, False)
            self.leftImg.append(img_left)
            self.rightImg.append(img_right)
        # Loads wing images facing left and right
        for num in range(1, 3):
            wingRight = pygame.image.load(f'platformer_assets/img/wings{num}.png')
            wingWidth = wingRight.get_rect().width
            wingLeft = pygame.transform.flip(wingRight, True, False)
            self.rightImg.append((wingRight, wingWidth))
            self.leftImg.append((wingLeft, wingWidth))
        self.image = self.rightImg[0]
        self.hitbox = pygame.transform.scale(self.image, (45, 80))
        self.rect = self.hitbox.get_rect()
        self.width = self.hitbox.get_rect().width
        self.height = self.hitbox.get_rect().height
        self.rect.x = x
        self.rect.y = y

    # Takes damage if damage-taking is not on cooldown
    def takeDamage(self):
        if self.damageCD == 0:
            if sound:
                damageSound.play()
            self.health -= 1
            self.damageCD = 1

    # Tracks damage cooldown for player and draws player
    def update(self):
        mobLayer.blit(self.image, (self.rect.x - 7, self.rect.y - 10))
        if self.damageCD != 0:
            self.damageCD += 1
            if self.damageCD >= FPS:
                self.damageCD = 0
        for heart in range(self.health):
            menuLayer.blit(self.heart, (400 + heart * 38, 3))


# Variables ------------------------------------------------------------------------------------------------------------
# Game constants
width = 1000
height = 900
FPS = 60
tileCount = 20
tileSize = int(width / tileCount)
# Load images

# World
menuImg = pygame.image.load('platformer_assets/background/menu.jpeg')
backgroundImg = pygame.image.load('platformer_assets/background/night.jpeg')
customLevelData = []
# Buttons


# Mobs
# Pygame variables
clock = pygame.time.Clock()
keyPressed = pygame.key.get_pressed()
font = pygame.font.SysFont('Times New Roman', 15)
buttonFont = pygame.font.Font('platformer_assets/simply_rounded.ttf', 50)
smallFont = pygame.font.Font('platformer_assets/simply_rounded.ttf', 25)

damageSound = pygame.mixer.Sound('platformer_assets/audio/damage.ogg')
damageSound.set_volume(2)
buttonClick = pygame.mixer.Sound('platformer_assets/audio/click.ogg')
deathSound = pygame.mixer.Sound('platformer_assets/audio/death.ogg')
jumpSound = pygame.mixer.Sound('platformer_assets/audio/jump.ogg')
walkSound = pygame.mixer.Sound('platformer_assets/audio/walk.ogg')
finishSound = pygame.mixer.Sound('platformer_assets/audio/finish.ogg')
coinSound = pygame.mixer.Sound('platformer_assets/audio/coin.ogg')

walkChannel = pygame.mixer.Channel(5)

# Music tracks
music = pygame.mixer.music
music.set_volume(0.25)

# Game variables
levelSelect = pygame.sprite.Group()
gamestate = 0
mouseDown = False
sound = True
musicControl = True
fpsCounter = True
pause = False
# Debug
debug = False
cheats = False

# Creates player class
# Exists so imgList isn't undefined. Would be fixed by moving imgList into player class
player = Player(150, height - 500)

# Buttons----------------------------------------------
buttons = pygame.sprite.Group()
# Main menu
start = Button(width // 2 - 4 * tileSize, height // 5, 'Levels', (8 * tileSize, 2 * tileSize), buttonFont)
customLevelBtn = Button(width // 2 - 4 * tileSize, 2 * height // 5, 'Custom Level', (8 * tileSize, 2 * tileSize),
                        buttonFont)
settings = Button(width // 2 - 4 * tileSize, 3 * height // 5, 'Settings', (8 * tileSize, 2 * tileSize), buttonFont)
quitBtn = Button(width // 2 - 4 * tileSize, 4 * height // 5, 'Quit', (8 * tileSize, 2 * tileSize), buttonFont)
# Settings menu
pauseBtn = Button(width - 125, 10, 'Pause', (2 * tileSize, tileSize), smallFont)
soundToggle = toggleButton(750, 200, 'SoundFX ON/OFF')
musicToggle = toggleButton(750, 275, 'Music ON/OFF')
fpsToggle = toggleButton(750, 350, 'FPS Counter ON/OFF')
back = Button(width // 2 - 4 * tileSize, 3 * height // 5, 'Back', (8 * tileSize, 2 * tileSize), buttonFont)
mainMenu = Button(width // 2 - 4 * tileSize, 4 * height // 5, 'Main Menu', (8 * tileSize, 2 * tileSize), buttonFont)
# Level buttons
restart = Button(width // 2 - 4 * tileSize, 3.5 * height // 5, 'Restart', (8 * tileSize, 2 * tileSize), buttonFont)
nextLevel = Button(width // 2 - 4 * tileSize, 3.5 * height // 5, 'Next Level', (8 * tileSize, 2 * tileSize), buttonFont)

# Player variables-------------------------------------
moveIndex = 0
walkCounter = 0
yVel = 0
yAccel = 1
imgList = player.rightImg
onBlock = False
# Addons
wings = True
wingCounter = 0
fly = False

# Create screen
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption('Plateformer Game')
# Surfaces
mobLayer = pygame.surface.Surface((width, height)).convert_alpha()
menuLayer = pygame.surface.Surface((width, height)).convert_alpha()

# Startup sounds
startupSound = pygame.mixer.Sound('platformer_assets/audio/startup.ogg')
startupSound.set_volume(0.1)
startupSound.play()

# Main game loop -------------------------------------------------------------------------------------------------------
while True:
    # Stops music if not inside a game level or music is turned off
    if gamestate != 1 or not musicControl:
        if gamestate != 2 and music.get_busy():
            music.stop()
    # Stops walk sound effects if not inside a game level or sound effects are turned off
    if gamestate != 1 or not sound:
        if walkChannel.get_busy():
            walkSound.stop()

    # Resets each layer
    mobLayer.fill((0, 0, 0, 0))
    menuLayer.fill((0, 0, 0, 0))

    # Sets background for menu and game level
    if gamestate != 0 and gamestate != 0.2 and gamestate != 0.1:
        screen.blit(backgroundImg, (0, 0))
    else:
        screen.blit(menuImg, (0, 0))

    # Gets keypresses for shift jumping
    keyPressed = pygame.key.get_pressed()
    # Resets mouseclick status
    if mouseDown:
        mouseDown = False
    # Checks queue for actionable events
    for event in pygame.event.get():
        # Quits game if user clicks x button
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Player jump inputs
        if event.type == pygame.KEYDOWN and gamestate == 1:
            # Makes player jump
            if event.key == pygame.K_SPACE and onBlock:
                # Plays game sounds
                if sound:
                    jumpSound.play()
                # Jumps slightly lower when holding shift
                if keyPressed[pygame.K_LSHIFT]:
                    yVel = -16
                # Jumps higher when not holding shift
                else:
                    yVel = -21
            # Makes it so that player img changes as soon as a key is pressed
            if event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a]:
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    imgList = player.rightImg
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    imgList = player.leftImg
                player.image = imgList[1]
        # Updates mouse button status
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            mouseDown = True
    # Resets player jump status so that it is disabled unless there is a Y collision later on
    if onBlock:
        onBlock = False
    # Main Menu --------------------------------------------------------------------------------------------------------
    if gamestate == 0:
        # Checks which levels are unlocked when button is pressed and changes to levels screen
        if start.isPressed(mouseDown):
            gamestate = 0.1
            # Generates level select page
            levelSelect.empty()
            row = 0
            column = 0
            for level in range(len(levels)):
                if levels[level][1] == 0:
                    levelbtn = Button(75 + column * 450, 200 + row * 200, 'LOCKED', (8 * tileSize, 2 * tileSize),
                                      buttonFont)
                else:
                    levelbtn = Button(75 + column * 450, 200 + row * 200, f'Level {level + 1}',
                                      (8 * tileSize, 2 * tileSize), buttonFont)
                levelSelect.add(levelbtn)
                column += 1
                if column == 2:
                    column = 0
                    row += 1
        # If custom level button is pressed, checks for custom level file and attempts to load it.
        if customLevelBtn.isPressed(mouseDown):
            try:
                customLevelData = []
                with open(f'platformer_assets/levels/customlevel.txt', 'r') as lvlData:
                    for row in lvlData:
                        rowData = []
                        row = row.strip('\n').split(', ')
                        for block in row:
                            rowData.append(intCheck(block))
                        customLevelData.append(rowData)
            except FileNotFoundError:
                pass
            else:
                currentLevel = maxLvls
                currentLevelData = customLevelData
                gamestate = 0.5
        # Settings button, changes to settings screen
        if settings.isPressed(mouseDown):
            gamestate = 0.2
        # Exits the program
        if quitBtn.isPressed(mouseDown):
            pygame.quit()
            sys.exit()
    # Level select page, loads the level pressed -----------------------------------------------------------------------
    if gamestate == 0.1:
        levelNum = 0
        for level in levelSelect.sprites():
            if level.isPressed(mouseDown):
                if levels[levelNum][1] != 0:
                    currentLevel = levelNum
                    currentLevelData = levels[currentLevel][0]
                    gamestate = 0.5
            levelNum += 1
        # Changes to main menu screen
        if mainMenu.isPressed(mouseDown):
            gamestate = 0

    # Settings menu ----------------------------------------------------------------------------------------------------
    if gamestate == 0.2:
        # Settings buttons
        pygame.draw.rect(menuLayer, (255, 204, 0), pygame.Rect(125, 125, 750, 750), 0, 50)
        sound = soundToggle.isPressed(mouseDown)
        musicControl = musicToggle.isPressed(mouseDown)
        fpsCounter = fpsToggle.isPressed(mouseDown)
        # Navigates back to main menu
        if mainMenu.isPressed(mouseDown):
            gamestate = 0

    # World loading, enters game after data is loaded ------------------------------------------------------------------
    if gamestate == 0.5:
        world = World(currentLevelData)
        player = Player(300, height - 500)
        gamestate = 1

    # Main game --------------------------------------------------------------------------------------------------------
    if gamestate == 1:
        # Starts background music if no music is playing, and if music is enabled
        if not pygame.mixer.music.get_busy() and musicControl:
            music.load(f'platformer_assets/audio/musicTrack{random.randint(1, 4)}.ogg')
            music.play(-1)
        # If the game is not paused, runs the game
        if not pause:
            # Updates all objects in the map
            world.objects.update()
            # Player and mob collisions, coin collisions, and finish line collision
            if pygame.sprite.spritecollide(player, world.damage, False) and not cheats:
                player.takeDamage()
            if pygame.sprite.spritecollide(player, world.coins, True):
                world.score += 1
                if sound:
                    coinSound.play()
            if pygame.sprite.spritecollide(player, world.finishFlags, False):
                gamestate = 2
                if sound:
                    finishSound.play()

            # Player movement
            moveY = 0
            moveX = 0
            keyPressed = pygame.key.get_pressed()
            # Move left
            if keyPressed[pygame.K_LEFT] or keyPressed[pygame.K_a]:
                moveX -= 5
                walkCounter += 1
                # Changes player image set to face left
                if imgList != player.leftImg:
                    imgList = player.leftImg
            # Move right
            if keyPressed[pygame.K_RIGHT] or keyPressed[pygame.K_d]:
                moveX += 5
                walkCounter += 1
                # Changes player image set to face right
                if imgList != player.rightImg:
                    imgList = player.rightImg
            # If player is not moving, changes player image to standing
            if moveX == 0:
                player.image = imgList[0]

            # Player movement animation
            elif walkCounter >= FPS / 6:
                walkCounter = 0
                if player.image != imgList[1]:
                    player.image = imgList[1]
                else:
                    player.image = imgList[2]

            # Gravity and falling
            # Fly mechanic, not really implemented. Only really used for testing at the moment
            if fly and keyPressed[pygame.K_SPACE]:
                if yVel > -10:
                    yVel -= 2
                else:
                    yVel = -10
            # Gliding if wings are enabled
            elif wings and keyPressed[pygame.K_SPACE]:
                if yVel < 0:
                    yVel += 1
                else:
                    # Wing open animation
                    if wingCounter < FPS // 10:
                        wingCounter += 1
                        mobLayer.blit(imgList[5][0], (player.rect.centerx - imgList[5][1] // 2, player.rect.y + 10))
                    else:
                        mobLayer.blit(imgList[6][0], (player.rect.centerx - imgList[6][1] // 2, player.rect.y + 10))
                    # Gliding fall speed
                    yVel = 3
            else:
                # Wing close animation
                if wings and wingCounter > 0:
                    wingCounter -= 1
                    mobLayer.blit(imgList[5][0], (player.rect.centerx - imgList[5][1] // 2, player.rect.y + 10))
                if yVel < 10:
                    yVel += 1
                else:
                    yVel = 10

            moveY = yVel

            # Player collision checks
            # Moving blocks collision
            for movingBlock in world.movingBlocks:
                # Horizontal collisions
                if movingBlock.rect.colliderect(player.rect.x + moveX, player.rect.y, player.width, player.height):
                    # Checks for collisions with left side of moving block
                    if player.rect.right + moveX - movingBlock.rect.left < 15:
                        moveX = movingBlock.rect.left - player.rect.right
                    # Checks for collision with right side of moving block
                    if movingBlock.rect.right - player.rect.left + moveX < 15:
                        moveX = movingBlock.rect.right - player.rect.left
                # Vertical collisions
                elif movingBlock.rect.colliderect(player.rect.x, player.rect.y + moveY, player.width, player.height):
                    # Checks for collision with bottom of moving block
                    if movingBlock.rect.bottom - player.rect.top + moveY < 15:
                        yVel = 0
                        moveY = movingBlock.rect.bottom - player.rect.top
                    # Checks for collision with top of moving block
                    elif player.rect.bottom + moveY - movingBlock.rect.top < 20:
                        moveY = movingBlock.rect.top - player.rect.bottom - 1
                        onBlock = True
                        # Allows player to move horizontally with block if they are atop it
                        if movingBlock.axis == 0:
                            moveX += movingBlock.direction

            # Collisions for stationary blocks
            for block in world.blocks:
                # Horizontal collision
                if block.rect.colliderect(player.rect.x + moveX, player.rect.y, player.width, player.height):
                    moveX = 0
                # Vertical collision
                elif block.rect.colliderect(player.rect.x, player.rect.y + moveY, player.width, player.height):
                    # Calculates collision and movement if player is moving up
                    if yVel < 0:
                        moveY = block.rect.bottom - player.rect.top
                        yVel = 0
                    # Calculates collision and movement if player is moving down
                    elif yVel >= 0:
                        moveY = block.rect.top - player.rect.bottom
                        onBlock = True
            # Changes player image for falling and jumping
            if yVel <= 0:
                player.image = imgList[3]
            elif yVel > 0 and not onBlock:
                player.image = imgList[4]
            # Plays walking sound effects if sound is enabled and player is walking along ground
            if sound and onBlock and abs(moveX) > 1:
                if not walkChannel.get_busy():
                    walkChannel.play(walkSound)
            elif walkChannel.get_busy():
                walkSound.stop()

            # Camera movement, keeps player on center left of screen unless map is at edges
            if world.cameraPos + moveX < 0 or world.cameraPos + moveX > 3000:
                player.rect.x += moveX
            # If the player is not at center left, allows player to move there first before locking camera
            elif moveX < 0 and player.rect.x + moveX > 375:
                player.rect.x += moveX
            elif moveX > 0 and player.rect.x + moveX < 375:
                player.rect.x += moveX
            else:
                for obj in world.objects:
                    obj.rect.x -= moveX
                world.cameraPos += moveX

            # If player has no more health, kills player
            player.rect.y += moveY
            if player.health <= 0:
                # Plays death sound if player dies
                if sound:
                    deathSound.play()
                gamestate = -1

            # Pause button
            if pauseBtn.isPressed(mouseDown):
                pause = True


        # Pause menu
        else:
            # Background box for pause menu
            pygame.draw.rect(menuLayer, (255, 204, 0), pygame.Rect(125, 125, 750, 750), 0, 50)
            # Toggle buttons
            sound = soundToggle.isPressed(mouseDown)
            musicControl = musicToggle.isPressed(mouseDown)
            fpsCounter = fpsToggle.isPressed(mouseDown)
            # Shows what level is currently active, if the level is a custom level, draws 'Custom Level'
            if currentLevelData != customLevelData:
                menuLayer.blit(buttonFont.render(f'Level {currentLevel + 1}', True, (255, 255, 255)),
                               (width // 2 - 75, 2.5 * height // 5))
            else:
                menuLayer.blit(buttonFont.render('Custom Level', True, (255, 255, 255)),
                               (width // 2 - 150, 2.5 * height // 5))

            # Restart, back to game, and main menu buttons
            if restart.isPressed(mouseDown):
                gamestate = 0.5
                pause = False
            if back.isPressed(mouseDown):
                pause = False
            if mainMenu.isPressed(mouseDown):
                gamestate = 0
                pause = False
        # Draws a grid for debugging, and draws player hitbox
        if debug:
            drawGrid(world.cameraPos)
            pygame.draw.rect(screen, (255, 255, 255), player.rect, 2)

    # Victory screen ---------------------------------------------------------------------------------------------------
    if gamestate == 2:
        # Displays score achieved for the level, and draws main menu and next level button
        pygame.draw.rect(menuLayer, (255, 204, 0), pygame.Rect(275, 500, 450, 350), 0, 50)
        menuLayer.blit(buttonFont.render(f'Score: {world.score}', True, (255, 255, 255)),
                       (width // 2 - 100, 2.75 * height // 5))
        if mainMenu.isPressed(mouseDown):
            if currentLevel < maxLvls - 1:
                currentLevel += 1
                levels[currentLevel][1] = 1
            gamestate = 0
        # Next level button is not drawn if there are no proceeding levels
        if currentLevel < maxLvls - 1 and nextLevel.isPressed(mouseDown):
            currentLevel += 1
            levels[currentLevel][1] = 1
            currentLevelData = levels[currentLevel][0]
            gamestate = 0.5
    # Death screen -----------------------------------------------------------------------------------------------------
    if gamestate == -1:
        # Changes player image to ghost
        player.image = player.ghost
        # Displays restart and main menu buttons
        if restart.isPressed(mouseDown):
            gamestate = 0.5
        if mainMenu.isPressed(mouseDown):
            gamestate = 0

    # Updates player and draws world if the current game state is not a menu
    if gamestate == 1 or gamestate == -1 or gamestate == 2:
        world.drawLvl()
        player.update()

    # Updates buttons and draws layers
    buttons.update()
    screen.blit(mobLayer, (0, 0))
    screen.blit(menuLayer, (0, 0))

    # Displays FPS counter if the option is toggled on
    if fpsCounter:
        displayFPS(screen, (0, 0), font, (255, 255, 255), FPS)
    else:
        pygame.display.update()
        clock.tick(FPS)
