import pygame
import math

pygame.init()

# ==================================
# WINDOW
# ==================================

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buttered Toast Simulation")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# ==================================
# CONSTANTS
# ==================================

PIXELS_PER_METER = 180

floor_y = 700

toast_width = 120
toast_height = 30

table_height = 0.75

# ==================================
# RESET
# ==================================

def reset():

    global x
    global y
    global angle
    global falling
    global target_angle

    x = 700

    table_y = floor_y - table_height * PIXELS_PER_METER

    y = table_y - 20

    angle = 0
    falling = True

    # 논문 결과 근사
    if table_height <= 0.75:

        target_angle = 180

    elif table_height >= 3.0:

        target_angle = 316

    else:

        target_angle = (
            180
            + (316 - 180)
            * (table_height - 0.75)
            / (3.0 - 0.75)
        )

reset()

# ==================================
# MAIN LOOP
# ==================================

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                reset()

            if event.key == pygame.K_UP:

                table_height = min(
                    3.0,
                    table_height + 0.25
                )

                reset()

            if event.key == pygame.K_DOWN:

                table_height = max(
                    0.5,
                    table_height - 0.25
                )

                reset()

    table_y = floor_y - table_height * PIXELS_PER_METER

    # =============================
    # MOTION
    # =============================

    if falling:

        distance = floor_y - table_y

        y += 4

        angle -= target_angle / (distance / 4)

    # =============================
    # LANDING
    # =============================

    if y >= floor_y - toast_height:

        y = floor_y - toast_height

        angle = -target_angle

        falling = False

    # =============================
    # RECTANGLE
    # =============================

    rad = math.radians(angle)

    ux = math.cos(rad)
    uy = math.sin(rad)

    vx = -uy
    vy = ux

    hw = toast_width / 2
    hh = toast_height / 2

    c1 = (
        x + ux * hw + vx * hh,
        y + uy * hw + vy * hh
    )

    c2 = (
        x - ux * hw + vx * hh,
        y - uy * hw + vy * hh
    )

    c3 = (
        x - ux * hw - vx * hh,
        y - uy * hw - vy * hh
    )

    c4 = (
        x + ux * hw - vx * hh,
        y + uy * hw - vy * hh
    )

    # =============================
    # DRAW
    # =============================

    screen.fill((245,245,245))

    # floor

    pygame.draw.line(
        screen,
        (200,0,0),
        (0,floor_y),
        (WIDTH,floor_y),
        5
    )

    # table

    pygame.draw.line(
        screen,
        (0,0,0),
        (150,table_y),
        (700,table_y),
        6
    )

    # bread

    pygame.draw.polygon(
        screen,
        (205,170,125),
        [c1,c2,c3,c4]
    )

    # butter surface

    butter = [

        c1,
        c2,

        (
            c2[0] + vx*8,
            c2[1] + vy*8
        ),

        (
            c1[0] + vx*8,
            c1[1] + vy*8
        )
    ]

    pygame.draw.polygon(
        screen,
        (255,220,40),
        butter
    )

    pygame.draw.polygon(
        screen,
        (90,60,30),
        [c1,c2,c3,c4],
        2
    )

    # info

    info = [

        f"Table Height : {table_height:.2f} m",

     f"Animation Angle : {angle:.1f} deg",

    

    "Paper Result (0.75m) : ~180 deg",

    "Paper Result (3.0m) : ~316.6 deg",

    "UP / DOWN : Change Height",

    "R : Reset"
    ]

    for i,text in enumerate(info):

        img = font.render(
            text,
            True,
            (0,0,0)
        )

        screen.blit(
            img,
            (20,20+i*45)
        )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()