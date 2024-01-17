import pygame
import time
import math

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
falling_piece_pos = [0, 0, 0] # x, y, rot
falling_piece_color = 1

falling_piece = piece_lib[2]

# format: [row_index, anim_timestep]
active_row_anims = []

# calculate proper render area size based on config
render_area_size = (border_thickness * 2 + border_margins * 2 + level_size[0] * (tile_size + tile_margins * 2), border_thickness * 2 + border_margins * 2 + level_size[1] * (tile_size + tile_margins * 2))
render_area_border = (res[0] // 2 - render_area_size[0] // 2, res[1] // 2 - render_area_size[1] // 2, render_area_size[0], render_area_size[1])

current_time = time.time()
delta_time = 0

# == init ==

pygame.init()

win = pygame.display.set_mode(res, vsync=1)

for y in range(level_size[1]):
    row = []
    level.append(row)

    for x in range(level_size[0]):
        row.append(0)

# == update code ==

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

def world_to_screen_space(p):
    return (render_area_border[0] + border_thickness + border_margins + tile_margins + p[0] * (tile_size + tile_margins * 2), render_area_border[1] + border_thickness + border_margins + tile_margins + p[1] * (tile_size + tile_margins * 2))

def game_update():
    # events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()

    # user input
        
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        falling_piece_pos[2] = (falling_piece_pos[2] + 1) % 4

    elif keys[pygame.K_d]:
        falling_piece_pos[2] = (falling_piece_pos[2] - 1) % 4

    elif keys[pygame.K_UP]:
        pass

    elif keys[pygame.K_DOWN]:
        pass

    # main update

    check_rows()

def draw_frame():
    update_anim()
    
    win.fill(none_color)

    # draw border
    pygame.draw.rect(win, border_color, render_area_border)
    pygame.draw.rect(win, none_color, (render_area_border[0] + border_thickness, render_area_border[1] + border_thickness, render_area_border[2] - border_thickness * 2, render_area_border[3] - border_thickness * 2))

    # draw level

    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            # TODO: render active anims

            if not tile == 0:
                pos = world_to_screen_space((x, y))
                pygame.draw.rect(win, color_lib[tile - 1], (pos[0], pos[1], tile_size, tile_size))

    # draw falling piece

    if not len(falling_piece) == 0:
        for tile_pos in translate_falling_piece():
            pos = world_to_screen_space(tile_pos)
            pygame.draw.rect(win, color_lib[falling_piece_color - 1], (pos[0], pos[1], tile_size, tile_size))

    pygame.display.flip()

# == game loop ==

while True:
    delta_time = time.time() - current_time
    current_time = time.time()

    # if delta_time == 0:
    #     continue

    game_update()

    draw_frame()