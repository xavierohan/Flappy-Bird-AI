import pygame
import os
import random

WIN_WIDTH = 600
WIN_HEIGHT = 800

BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]  # making img size x2
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))


class Bird:
    IMGS = BIRD_IMAGES
    MAX_ROT = 25  # Tilt of the bird
    ROT_VEL = 20  # Rotation on each frame
    ANIMATION_TIME = 5  # Time for each bird animation

    def __init__(self, x, y):
        # x, y - starting pos
        self.x = x
        self.y = y
        self.tilt = 0  # starting at tilt 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5  # -ve velocity -- as top left corner is (0,0) , so to move upwards needs a -ve velocity
        self.tick_count = 0  # keeps track of last jump
        self.height = self.y  # keeps track of where the bird jumped from

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 2 * self.tick_count ** 2  # Tells how much movement,tick_count - rep how many sec the bird's been moving
        # d = -9 , -7 , -5 , .... , + ... - creates an arc for the bird

        if d >= 16:  # setting a bound
            d = 16

        if d < 0:
            d -= 2  # fine tunes the jump
        self.y = self.y + d  # changes y pos based on d

        if d < 0 or self.y < self.height + 50:  # moving upwards / on the downward arc
            if self.tilt < self.MAX_ROT:
                self.tilt = self.MAX_ROT
            else:  # moving downwards
                if self.tilt > -90:
                    self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        # decide which img to show based on img_count( flapping )

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:  # To not show flapping while the bird goes down
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)  # to rotate the bird
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(
            self.x, self.y)).center)  # to rotate wrt to birds center(above code rotates through top left corner)
        win.blit(rotated_image, new_rect.topleft)  # blit --> draw

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 0
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)  # to flip the pipe img upside down
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False  # For collision purposes
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)  # to get a rand no for top pipe
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):  # To move the pipe --> change x pos wrt to VEL
        self.x -= self.VEL

    def draw(self, win):  # to draw the pipes
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        mask_bird = bird.get_mask()  # to create a mask for the bird to detect collision with the pipe
        mask_top = pygame.mask.from_surface(self.PIPE_TOP)
        mask_bottom = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (
            self.x - bird.x, self.top - round(bird.y))  # how far away the 2 top left corners are from each other
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        collision_point_b = mask_bird.overlap(mask_bottom, bottom_offset)
        collision_point_t = mask_bird.overlap(mask_top, top_offset)

        if collision_point_b or collision_point_t:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMAGE.get_width()
    IMG = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):  # Creates a continuous cycle of 2 base images
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:  # Checks if base image x1 is off the screen
            self.x1 = self.x2 + self.WIDTH  # cycles x1 back to the screen
        if self.x2 + self.WIDTH < 0:  # Checks if base image x2 is off the screen
            self.x2 = self.x1 + self.WIDTH  # cycles x2 back to the screen

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base):
    win.blit(BACKGROUND_IMAGE, (0, 0))

    for pipe in pipes:  # can have multiple pipes in a window
        pipe.draw(win)
    base.draw(win)
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clk = pygame.time.Clock()
    score = 0
    run = True

    while run:
        clk.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    # bird.move()
                    bird.jump()
                else:
                    bird.move()

        # bird.jump()
        bird.move()
        rem_pipe = []
        add_pipe = False

        for pipe in pipes:

            if pipe.collide(bird):
                pass

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # Check if pipe is off the screen (x pos + width of pipe)
                rem_pipe.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        for i in rem_pipe:
            pipes.remove(i)
        if bird.y + bird.img.get_height() >= 740:
            pygame.quit()

        base.move()
        draw_window(win, bird, pipes, base)
    pygame.quit()
    quit()


main()

#  Code inspired from https://github.com/techwithtim/NEAT-Flappy-Bird/blob/master/flappy_bird.py
