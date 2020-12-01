# Space Protector
# Developer: Matthew Quinn
# Artist: Sarah Fleischman
# Temporary universe background from:
# https://www.shutterstock.com/image-illustration/background-galaxy-stars-1177527625
# Sounds from zapsplat.com
# Made for Python 3.7.7 and PyGame 1.9.6
# Last updated: 6/19/20

import os, math, pygame, random

#initializes pygame modules
pygame.mixer.init(22050, -16, 2, 16)
pygame.init()

# error message if certain modules are unavailable
if not pygame.font:
    print('Error: fonts disabled.')
if not pygame.mixer:
    print('Error: sound disabled')

# changes window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (350, 50)



def cart_to_polar(x, y):
    # Precondition: an X or Y mouse position coordinate.
    # Output: a list containing the radius and the angle in degrees, 0 to 360.
    x -= (windowsize[0] / 2)
    y -= (windowsize[1] / 2)
    if x == 0:
        angle = 90.0
        r = y
    else:
        y_over_x = y / x
        radangle = math.atan(y_over_x)
        cosine_radangle = math.cos(radangle)
        r = x / cosine_radangle
        angle = math.degrees(radangle)
    if r >= 0:
        angle = angle * -1
    else:
        angle = 180 - angle
    if angle < 0:
        angle += 360
    return [r, angle]

def polar_to_cart(r, angle):
    # Precondition: an angle in degrees from 0 to 360, and a radius.
    # Output: the X and Y coordinates with the origin being the top left.
    radangle = math.radians(angle)
    r = abs(r)
    x = r * math.cos(radangle)
    y = r * math.sin(radangle)
    x += (windowsize[0] / 2)
    y -= (windowsize[1] / 2)
    return [x, abs(y)]

def radius_to_box_edge(angle):
    # Precondition: an angle in degrees from 0 to 360
    # Output: the radius given when it is extended to the edge of
    # the square screen.
    r = (math.sqrt(2) - 1) * math.sin(2*math.radians(angle))
    return (windowsize[0] / 2) * (abs(r) + 1)



class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.original = pygame.image.load('spaceship.png').convert_alpha()
        self.deathimage = pygame.image.load('deadspaceship.png').convert_alpha()
        self.deathframes = 0

    def update(self, mousepos):
        # checks to see if dead, and changes rotated sprite accordingly
        if endgame:
            self.deathframes = 20
        if self.deathframes > 0:
            self.deathframes -= 1
            return self.rotate(self.deathimage, mousepos)
        else:
            return self.rotate(self.original, mousepos)
        """if not endgame:
            return self.rotate(self.original, mousepos)
        else:
            return self.rotate(self.deathimage, mousepos)
        """
    def rotate(self, image, mousepos):
        # rotates the image and changes the top-left corner of the rectangle
        # based on the angle of rotation.
        # returns the new coordinates that account for rotation
        angle = cart_to_polar(mousepos[0], mousepos[1])[1] - 90
        constant = spaceship_rect.width / math.sqrt(2) - (spaceship_rect.width / 2)
        x_new = ((windowsize[0] - spaceship_rect.width) / 2)
        x_new -= (constant * abs(math.sin(2*math.radians(angle))))
        y_new = x_new
        self.image = pygame.transform.rotate(image, angle)
        return x_new, y_new

class Bullet(pygame.sprite.Sprite):
    def __init__(self, mousepos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_image
        self.showrect = self.origrect = bullet_rect
        self.dead = 0
        self.firedangle = cart_to_polar(mousepos[0], mousepos[1])[1]

        # sets initial distance from center
        self.distance = spaceship_rect.width * .4
        self.position = polar_to_cart(self.distance, self.firedangle)
        self.position[0] -= (self.origrect.width / 2)
        self.position[1] -= (self.origrect.height / 2)

        # plays sound effect when fired
        ##bullet_fire.play()
        bulletchannel.play(bullet_fire)

    def update(self):
        if not self.dead:
            self.position = polar_to_cart(self.distance, self.firedangle)

            # makes the position the center of the rectangle
            self.position[0] -= (self.origrect.width / 2)
            self.position[1] -= (self.origrect.height / 2)

            # dies when out of range (and fixes bullet bouncing glitch)
            if not 0.05 <= self.position[0] <= windowsize[0]:
                    self.dead = 1
            elif not 0.05 <= self.position[1] <= windowsize[1]:
                    self.dead = 1

            # distance from center changes each update cycle
            self.distance += bulletspeed

        else:
            # removes bullet from list
            bulletlist.remove(self)

        # updating current rectangle position
        self.showrect = self.origrect.move(self.position)

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = alien_image
        self.showrect = self.origrect = alien_rect
        self.dead = 0
        self.interactive = 1
        self.speed = alien_startspeed

        # random angle generator
        self.angle = .01 * random.randint(0, 99) + random.randint(0, 359)
        self.distance = radius_to_box_edge(self.angle)
        self.position = polar_to_cart(self.distance, self.angle)
        self.position[0] -= (self.origrect.width / 2)
        self.position[1] -= (self.origrect.height / 2)

    def update(self):
        if not self.dead:
            # updates alien position
            self.old_pos = self.position
            self.position = polar_to_cart(self.distance, self.angle)
            self.position[0] -= (self.origrect.width / 2)
            self.position[1] -= (self.origrect.height / 2)

            # distance to center changes each update cycle
            self.distance -= self.speed

            # dies when it gets too close to spaceship
            if self.distance <= 25:
                global endgame
                endgame = 1
                self.dead = 1

        else:
            # removes alien from list, death sprite
            alienlist.remove(self)
            deadalienlist.append(DeadAlien(self.position[0], self.position[1]))

        # if alien is going in wrong direction, it cannot be interacted with.
        # (fixes an error with how pygame deals with upward bound)
        # i.e. if alien is travelling upwards when position is above y = 350.
        if self.position[1] < ((windowsize[0] / 2) - 25) and self.old_pos[1] >= self.position[1]:
            self.interactive = 0
        else:
            self.interactive = 1

        # updating current rectangle position
        self.showrect = self.origrect.move(self.position)

class DeadAlien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.image = deadalien_image
        self.rect = deadalien_rect
        self.timeleft = aliendeathtime * fps
        self.position = (x, y)

    def update(self):
        # this timer reduces every frame. When 0, the sprite disappears.
        if self.timeleft == 0:
            deadalienlist.remove(self)
        else:
            self.timeleft -= 1

class LoadingBar(pygame.sprite.Sprite):
    def __init__(self):
        self.bar = pygame.image.load('bar_outline.png').convert_alpha()
        self.origbar = pygame.image.load('bar_outline.png').convert_alpha()
        self.progressrect = self.bar.get_rect()
        self.filled = 0

    def update(self, mach):
        # self.filled goes from 0 to 1 as increment increases. Resets when mach increases
        if mach == maxmach:
            self.filled = 1
        else:
            self.filled = (increment % (fps * secondsbetweenmach)) / (fps * secondsbetweenmach)

        # re-loads the bar
        self.bar = pygame.image.load('bar_outline.png').convert_alpha()

        # changes the width of the bar and draws it
        self.progressrect.width = 120 * self.filled
        pygame.draw.rect(self.bar, (255, 0, 0), pygame.Rect(0, 0, self.progressrect.width, 25))



# initializing the display. Note: all sprites should be squares.
windowsize = width, height = (750, 750)
screen = pygame.display.set_mode(windowsize)
background = pygame.image.load('universe.jpg').convert()
gamefont = pygame.font.SysFont('Verdana', 30)

# initializes window icon and title. Icon is randomly an alien or spaceship.
pygame.display.set_caption('Space Protector by Matthew Quinn')
if random.randint(0,1):
    icon = pygame.image.load('spaceship.png')
else:
    icon = pygame.image.load('alien.png')
pygame.display.set_icon(icon)

# initialize game objects
spaceship = Spaceship()
spaceship_rect = spaceship.image.get_rect()
bullet_image = pygame.image.load('bullet.png').convert_alpha()
bullet_rect = bullet_image.get_rect()
bulletlist = []
alien_image = pygame.image.load('alien.png').convert_alpha()
alien_rect = alien_image.get_rect()
alienlist = []
deadalien_image = pygame.image.load('deadalien.png').convert_alpha()
deadalien_rect = deadalien_image.get_rect()
deadalienlist = []
loadingbar = LoadingBar()

# initialize game sounds
bullet_fire = pygame.mixer.Sound('bullet_fire.wav')
alien_hit = pygame.mixer.Sound('alien_hit.wav')
mach_max = pygame.mixer.Sound('mach_max.wav')
bulletchannel = pygame.mixer.Channel(0)
alienchannel = pygame.mixer.Channel(1)
otherchannel = pygame.mixer.Channel(2)

# initializing variables
fps = 60
endgame = 0
score = 0
bulletiterator = 0
increment = 0
final_state = False
machtext_color = (255, 255, 255)

# variables that change the gameplay
bulletspeed = 10 # 10 ideal
i_avgalienspersec = 2 # 2 ideal. Can't be too high due to random module breaking
i_bulletspersec = 3 # 3 ideal
alien_startspeed = 2 # 2 is ideal
maxalienspeed = 3.5 # 3.5 is ideal
secondsbetweenmach = 20 # 20 ideal
speedincpersec = .0175 # .0175 ideal
aliendeathtime = .5 # .5 ideal
maxmach = 5 # 5 ideal, max 600.
godmode = 0 # 0 for normal gameplay, 1 for invulnerability



while not endgame:

    # 60fps cap
    pygame.time.Clock().tick(fps)

    # getting mouse position
    mousepos = pygame.mouse.get_pos()

    # collision detection for bullets and aliens. Changes alien speed
    for alien in alienlist:
        for bullet in bulletlist:
            if alien.showrect.colliderect(bullet.showrect) and alien.interactive:
                alienchannel.play(alien_hit)
                alien.dead = 1
                score += 1

    # changes mach, goes from 1 to maxmach (5).
    increment += 1
    mach = int(increment // (fps * secondsbetweenmach)) + 1
    if mach >= maxmach:
        mach = maxmach
        if not final_state:
            final_state = True
            otherchannel.play(mach_max)

    # if in maxmach, increases alien speed (up to a maximum)
    if mach == maxmach:
        alien_startspeed += (speedincpersec / fps)
        if alien_startspeed >= maxalienspeed:
            alien_startspeed = 3.5

    # changes rates based on mach
    avgalienspersec = (.5 * (mach - 1) * i_avgalienspersec) + i_avgalienspersec
    bulletspersec = (.5 * (mach - 1) * i_bulletspersec) + i_bulletspersec

    # random chance of spawning alien
    randint_limit = (fps / avgalienspersec) * 10
    if random.randint(1, int(randint_limit)) <= 10:
            alienlist.append(Alien())

    # checks if the mouse is clicked and if enough time has passed.
    bulletiterator += 1
    if pygame.mouse.get_pressed()[0] and bulletiterator >= fps / bulletspersec:
        bulletlist.append(Bullet(mousepos))
        bulletiterator = 0

    # updating sprite status
    for bullet in bulletlist:
        bullet.update()
    for alien in alienlist:
        alien.update()
    for deadalien in deadalienlist:
        deadalien.update()
    spaceship_coords = spaceship.update(mousepos)
    loadingbar.update(mach)

    # layers sprites onto screen
    # back to front: screen -> deadalien -> bullet -> spaceship -> alien
    # after alien, text -> bar (in different sections)
    screen.blit(background, background.get_rect())
    for deadalien in deadalienlist:
        screen.blit(deadalien.image, deadalien.rect.move(deadalien.position))
    for bullet in bulletlist:
        screen.blit(bullet.image, bullet.showrect)
    screen.blit(spaceship.image, spaceship_rect.move(spaceship_coords))
    for alien in alienlist:
        if alien.interactive:
            screen.blit(alien.image, alien.showrect)

    # text layer
    scoretext = gamefont.render('Score: ' + str(score), False, (255, 255, 255))
    screen.blit(scoretext, (0,0))
    if mach == maxmach:
        machtext_color = (255, 50, 50)
    machtext = gamefont.render('Mach: ' + str(mach), False, (machtext_color))
    screen.blit(machtext, (0,40))

    # loading bar layer
    screen.blit(loadingbar.bar, loadingbar.progressrect.move(3, 85))
    screen.blit(loadingbar.origbar, loadingbar.progressrect.move(3, 85))

    # updates display
    pygame.display.flip()

    # always sets endgame to 0 if godmode is activated
    if godmode:
        endgame = 0

    # stops if the game is exited
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

# endgame state when the player loses
while endgame:

    # stops sound playback
    pygame.mixer.stop()

    # stops if the game is exited
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
