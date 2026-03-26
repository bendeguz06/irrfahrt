import random
from collections import defaultdict

import pygame
import pygame.freetype

pygame.init()

WIDTH, HEIGHT = 1400, 900
FPS = 120
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Irrfahrt")
icon = pygame.image.load("rw_logo.png")
pygame.display.set_icon(icon)
FONT = pygame.freetype.Font("OpenSans-Bold.ttf", 18)

AXIS_COLOR = (0, 0, 0)
PALETTE = [
    (70,  130, 200),
    (200, 80,  70),
    (60,  170, 90),
    (180, 120, 200),
    (200, 150, 50),
    (50,  180, 180),
    (180, 80,  130),
    (100, 100, 200),
]
SUM_COLOR = (30, 30, 30)

PAD          = 10
TOOLBAR_H    = 44
LABEL_LEFT   = 40
LABEL_BOTTOM = 24

CENTER_W  = 700
CENTER_X  = (WIDTH - CENTER_W) // 2
CONTENT_Y = TOOLBAR_H + PAD
CENTER_H  = HEIGHT - CONTENT_Y - PAD
CENTER_Y  = CONTENT_Y
SIDE_W    = (WIDTH - CENTER_W - 4 * PAD) // 2

CENTER_PANEL = pygame.Rect(CENTER_X, CENTER_Y, CENTER_W, CENTER_H)

BTN_RESET_WALKS = pygame.Rect(PAD,            PAD, 140, TOOLBAR_H - 2 * PAD)
BTN_RESET       = pygame.Rect(2*PAD + 140,    PAD, 90,  TOOLBAR_H - 2 * PAD)
BTN_ADD         = pygame.Rect(3*PAD + 140+90, PAD, 160, TOOLBAR_H - 2 * PAD)


def side_panels(n):
    n_left  = (n + 1) // 2
    n_right = n // 2
    panels  = []

    def col_panels(n_col, x):
        if n_col == 0:
            return
        h = max(20, (CENTER_H - PAD * (n_col - 1)) // n_col)
        for i in range(n_col):
            panels.append(pygame.Rect(x, CENTER_Y + i * (h + PAD), SIDE_W, h))

    col_panels(n_left,  PAD)
    col_panels(n_right, WIDTH - PAD - SIDE_W)
    return panels


def graph_rect(panel):
    return pygame.Rect(
        panel.left + LABEL_LEFT,
        panel.top  + PAD,
        max(10, panel.width  - LABEL_LEFT - PAD),
        max(10, panel.height - LABEL_BOTTOM - PAD),
    )


def walk():
    return 1 if bool(random.getrandbits(1)) else -1


def draw_histogram(surface, counts, color, panel, label, show_y_axis=True):
    gr = graph_rect(panel)
    pygame.draw.rect(surface, (240, 240, 240), gr)

    if counts:
        keys      = list(counts.keys())
        min_x     = min(keys)
        max_x     = max(keys)
        span      = max(max_x - min_x, 1)
        max_count = max(counts.values())
        bar_width = gr.width / (span + 1)

        for pos, count in counts.items():
            bar_h = int((count / max_count) * (gr.height - 2))
            bx    = gr.left + int((pos - min_x) / (span + 1) * gr.width)
            by    = gr.bottom - bar_h
            pygame.draw.rect(surface, color, (bx + 1, by, max(1, int(bar_width) - 1), bar_h))

        label_count = min(7, span + 1)
        for i in range(label_count):
            val = min_x + int(i * span / max(label_count - 1, 1))
            lx  = gr.left + int((val - min_x) / (span + 1) * gr.width)
            FONT.render_to(surface, (lx - 8, gr.bottom + 3), str(val), AXIS_COLOR, size=12)

        if show_y_axis:
            for t in range(5):
                ty = gr.bottom - int(t / 4 * (gr.height - 2))
                tick_val = int(t / 4 * max_count)
                FONT.render_to(surface, (panel.left + 1, ty - 6), str(tick_val), AXIS_COLOR, size=11)


    pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.top),    (gr.left,  gr.bottom), 2)
    pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.bottom), (gr.right, gr.bottom), 2)

    FONT.render_to(surface, (gr.left + 2, panel.top + 2), label, color, size=13)


def draw_button(surface, rect, text, hover=False):
    bg = (170, 170, 170) if hover else (210, 210, 210)
    pygame.draw.rect(surface, bg, rect, border_radius=4)
    pygame.draw.rect(surface, AXIS_COLOR, rect, 1, border_radius=4)
    FONT.render_to(surface, (rect.x + 8, rect.y + 6), text, AXIS_COLOR, size=16)


positions = [0] * 4
counts    = [defaultdict(int) for _ in range(4)]

loop  = True
clock = pygame.time.Clock()

while loop:
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                loop = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if BTN_RESET_WALKS.collidepoint(mx, my):
                positions = [0] * len(positions)
                counts    = [defaultdict(int) for _ in range(len(positions))]
            elif BTN_RESET.collidepoint(mx, my):
                positions = [0] * 4
                counts    = [defaultdict(int) for _ in range(4)]
            elif BTN_ADD.collidepoint(mx, my):
                positions.append(0)
                counts.append(defaultdict(int))

    n = len(positions)
    for i in range(n):
        positions[i] += walk()
        counts[i][positions[i]] += 1

    all_keys   = set().union(*counts)
    sum_counts = {x: sum(c.get(x, 0) for c in counts) for x in all_keys}

    panels = side_panels(n)

    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (225, 225, 225), (0, 0, WIDTH, TOOLBAR_H))
    draw_button(screen, BTN_RESET_WALKS, "Reset Walks",  BTN_RESET_WALKS.collidepoint(mx, my))
    draw_button(screen, BTN_RESET,       "Reset",         BTN_RESET.collidepoint(mx, my))
    draw_button(screen, BTN_ADD,         "+ Add Walker",  BTN_ADD.collidepoint(mx, my))

    for i in range(n):
        draw_histogram(screen, counts[i], PALETTE[i % len(PALETTE)], panels[i],
                       f"W{i+1} X={positions[i]}", show_y_axis=False)

    draw_histogram(screen, sum_counts, SUM_COLOR, CENTER_PANEL, "Sum", show_y_axis=True)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
