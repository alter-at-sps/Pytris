import pygame
import time
import math
import random

# == config ==

res = (1280, 720)

desend_speed = 5
level_size = (10, 20)

tile_size = 15
tile_margins = 2

border_thickness = 15
border_margins = 4

border_color = (200, 200, 200)
none_color = (16, 16, 16)

# contains positions of tiles relative to the center of rotation of a piece
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

color_lib = [
    (102, 255, 255),
    (255, 0, 0),
    (128, 255, 0),
    (127, 0, 255),
    (255, 128, 0)
]

# == global vars ==

# 0 - empty
# not 0 - filled; value represents color of the tile
level = [] # row major layout

# points to the current piece thats falling
falling_piece = []
falling_piece_pos = [0, 0, 0] # x, y, rot (in world coord system; starting from top-left)
falling_piece_color = 0

# format: [row_index, anim_timestep]
active_row_anims = []

screenshake_amount = 0
screenshake_offset = (.0, .0)

# calculate proper render area size based on config
render_area_size = (border_thickness * 2 + border_margins * 2 + level_size[0] * (tile_size + tile_margins * 2), border_thickness * 2 + border_margins * 2 + level_size[1] * (tile_size + tile_margins * 2))
render_area_border = (res[0] // 2 - render_area_size[0] // 2, res[1] // 2 - render_area_size[1] // 2, render_area_size[0], render_area_size[1])

current_time = time.time()
delta_time = 0

update_timestamp = time.time()

was_pressed = [ False, False, False, False, False ]

# == init ==

pygame.init()

win = pygame.display.set_mode(res, vsync=1)

for y in range(level_size[1]):
    row = []
    level.append(row)

    for x in range(level_size[0]):
        # if y == 19 and x != 0:
        #     row.append(1)
        # else:
        row.append(0)

# == update code ==

# queues row completion animation
def queue_row_anim(i):
    active_row_anims.append([i, 0.0])

# called after a row animation finishes
def on_row_anim_finished(i):
    # offset level
    for j in range(i, 0, -1):
        if not j == 0:
            level[j] = level[j - 1]
        else:
            new_row = []
            level[j] = new_row

            for i in range(level_size[0]):
                new_row.append(0)

    # offset active anims
    for anim in active_row_anims:
        if anim[0] > i:
            anim[0] -= 1

# update animation timestamp
def update_anim():
    for anim in active_row_anims:
        anim[1] += delta_time

        if anim[1] > 1.0:
            active_row_anims.remove(anim)

# check rows for filled rows and queue animation
def check_rows():
    for i, row in enumerate(level):
        fully_filled = True

        for tile in row:
            if tile == 0:
                fully_filled = False
        
        if fully_filled:
            on_row_anim_finished(i) # temp until anims

# translates piece position local coords to world coords
def translate_falling_piece():
    # copy to avoid modifying the lib
    tiles = falling_piece.copy()

    for i in range(len(tiles)):
        # rotate piece
        for j in range(falling_piece_pos[2]):
            tiles[i] = (tiles[i][1], -tiles[i][0]) # 90 degree vector rotation

        # translate piece

        tiles[i] = (tiles[i][0] + falling_piece_pos[0], tiles[i][1] + falling_piece_pos[1])

    return tiles

# checks if the current falling piece is in a valid position
def check_falling_piece():
    tiles = translate_falling_piece()

    for tile in tiles:
        if tile[0] < 0 or tile[0] >= level_size[0]:
            return False

        if tile[1] < 0 or tile[1] >= level_size[1]:
            return False
        
        if not level[tile[1]][tile[0]] == 0:
            return False

    return True

# world coords to screen space (pixel) coords
def world_to_screen_space(p):
    return (render_area_border[0] + border_thickness + border_margins + tile_margins + p[0] * (tile_size + tile_margins * 2), render_area_border[1] + border_thickness + border_margins + tile_margins + p[1] * (tile_size + tile_margins * 2))

p_index = 0

def pick_next_piece():
    global p_index
    global falling_piece
    global falling_piece_pos
    global falling_piece_color

    falling_piece = piece_lib[p_index % len(piece_lib)]
    falling_piece_color = (p_index % (len(color_lib))) + 1

    falling_piece_pos = [level_size[0] // 2 - 1, 2, 0]

    p_index += 1

def process_user():
    global falling_piece
    global falling_piece_pos
    global falling_piece_color
    global screenshake_amount
    global was_pressed

    # events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()

    # user input
        
    keys = pygame.key.get_pressed()

    # some delicious movement code spaghetti
    if keys[pygame.K_a] and was_pressed[0] == False:
        was_pressed[0] = True
        falling_piece_pos[0] -= 1
        if not check_falling_piece():
            falling_piece_pos[0] += 1

    if not keys[pygame.K_a] and was_pressed[0]:
        was_pressed[0] = False

    if keys[pygame.K_d] and was_pressed[1] == False:
        was_pressed[1] = True
        falling_piece_pos[0] += 1
        if not check_falling_piece():
            falling_piece_pos[0] -= 1

    if not keys[pygame.K_d] and was_pressed[1]:
        was_pressed[1] = False

    if keys[pygame.K_e] and was_pressed[2] == False and not falling_piece == piece_lib[0]:
        was_pressed[2] = True
        falling_piece_pos[2] = (falling_piece_pos[2] - 1) % 4
        if not check_falling_piece():
            falling_piece_pos[2] = (falling_piece_pos[2] + 1) % 4

    if not keys[pygame.K_e] and was_pressed[2]:
        was_pressed[2] = False

    if keys[pygame.K_q] and was_pressed[3] == False and not falling_piece == piece_lib[0]:
        was_pressed[3] = True
        falling_piece_pos[2] = (falling_piece_pos[2] + 1) % 4
        if not check_falling_piece():
            falling_piece_pos[2] = (falling_piece_pos[2] - 1) % 4

    if not keys[pygame.K_q] and was_pressed[3]:
        was_pressed[3] = False

    if keys[pygame.K_s] and was_pressed[4] == False:
        was_pressed[4] = True
        screenshake_amount += 20

        while check_falling_piece():
            falling_piece_pos[1] += 1

        falling_piece_pos[1] -= 1

    if not keys[pygame.K_s] and was_pressed[4]:
        was_pressed[4] = False

def game_update():
    global falling_piece
    global falling_piece_pos
    global falling_piece_color
    global screenshake_amount

    check_rows()

    falling_piece_pos[1] += 1
    if not check_falling_piece():
        falling_piece_pos[1] -= 1

        tiles = translate_falling_piece()

        for tile in tiles:
            level[tile[1]][tile[0]] = falling_piece_color

        pick_next_piece()

        # check game over
        if not check_falling_piece():
            pygame.quit()
            exit()

def draw_frame():
    global falling_piece_pos
    global screenshake_amount
    global screenshake_offset

    # per draw updates

    update_anim()

    screenshake_amount = max(screenshake_amount - delta_time * 40, 0)
    screenshake_offset = (random.random() * 2 - 1, random.random() * 2 - 1)

    shake = (screenshake_offset[0] * screenshake_amount, screenshake_offset[1] * screenshake_amount)

    # rendering
    
    win.fill(none_color)

    # draw border
    pygame.draw.rect(win, border_color, (render_area_border[0] + shake[0], render_area_border[1] + shake[1], render_area_border[2], render_area_border[3]))
    pygame.draw.rect(win, none_color, (render_area_border[0] + border_thickness + shake[0], render_area_border[1] + border_thickness + shake[1], render_area_border[2] - border_thickness * 2, render_area_border[3] - border_thickness * 2))

    # draw level

    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            # TODO: render active anims

            if not tile == 0:
                pos = world_to_screen_space((x, y))
                pygame.draw.rect(win, color_lib[tile - 1], (pos[0] + shake[0], pos[1] + shake[1], tile_size, tile_size))

    # draw piece ghost
            
    if not len(falling_piece) == 0:
        old_falling_pos = falling_piece_pos.copy()

        while check_falling_piece():
            falling_piece_pos[1] += 1

        falling_piece_pos[1] -= 1

        for tile_pos in translate_falling_piece():
            pos = world_to_screen_space(tile_pos)
            col = color_lib[falling_piece_color - 1]
            pygame.draw.rect(win, (max(col[0] - 96, 0), max(col[1] - 96, 0), max(col[2] - 96, 0)), (pos[0] + shake[0], pos[1] + shake[1], tile_size, tile_size))

        falling_piece_pos = old_falling_pos

    # draw falling piece

    if not len(falling_piece) == 0:
        for tile_pos in translate_falling_piece():
            pos = world_to_screen_space(tile_pos)
            pygame.draw.rect(win, color_lib[falling_piece_color - 1], (pos[0] + shake[0], pos[1] + shake[1], tile_size, tile_size))

    pygame.display.flip()

# == game loop ==

pick_next_piece()

while True:
    delta_time = time.time() - current_time
    current_time = time.time()

    # update only every timestep
    if time.time() - update_timestamp >= 0.5:
        update_timestamp = time.time()

        game_update()

    # render and pull input as fast as possible (or at vsync)
    process_user()
    draw_frame()