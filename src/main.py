import pygame
import time
import math

# == config ==

res = (1280, 720)

desend_speed = 5
level_size = (10, 20)

piece_lib = [
    [ # square
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1)
    ],
    [ # I piece
        (0, -1),
        (0, 0),
        (0, 1),
        (0, 2)
    ],
    [ # L piece
        (0, 0),
        (1, 0),
        (0, 1),
        (0, 2)
    ],
    [ # mirrored L piece
        (0, 0),
        (-1, 0),
        (0, 1),
        (0, 2)
    ],
    [ # Z piece
        (-1, 1),
        (0, 1),
        (0, 0),
        (1, 0)
    ],
    [ # mirrored Z piece
        (1, 1),
        (0, 1),
        (0, 0),
        (-1, 0)
    ],
    [ # T piece
        (0, 0),
        (-1, 0),
        (1, 0),
        (0, -1)
    ]
]

# == init ==

pygame.init()

win = pygame.display.set_mode(res, vsync=1)

# == update code ==

# 0 - empty
# not 0 - filled; value represents color of the tile
level = [] # row major layout

for y in range(level_size[0]):
    row = []
    level.append(row)

    for x in row:
        level.append(0)

# format: [row_index, anim_timestep]
active_row_anims = []

current_time = time.time()
delta_time = 0

# queues row completion animation
def queue_row_anim(i):
    active_row_anims.append([i, 0.0])

# called after a row animation finishes
def on_row_anim_finished(i):
    # offset level
    for j in range(i + 1, len(level)):
        level[j] = level[j + 1]

    # offset active anims
    for anim in active_row_anims:
        if anim[0] > i:
            anim[0] -= 1

def update_anim():
    for anim in active_row_anims:
        anim[1] += delta_time

        if anim[1] > 1.0:
            active_row_anims.remove(anim)

def check_rows():
    for i, row in enumerate(level):
        fully_filled = True

        for tile in row:
            if tile == 0:
                fully_filled = False
        
        if fully_filled:
            queue_row_anim(i)

def game_update():
    # events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()

    # user input
        
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        pass

    elif keys[pygame.K_s]:
        pass

    elif keys[pygame.K_UP]:
        pass

    elif keys[pygame.K_DOWN]:
        pass

    # main update

    check_rows()

def draw_frame():
    win.fill((16, 16, 16))

    update_anim()

    pygame.display.flip()

# == game loop ==

while True:
    delta_time = time.time() - current_time
    current_time = time.time()

    # if delta_time == 0:
    #     continue

    game_update()

    draw_frame()