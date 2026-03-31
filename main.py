import math
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

BTN_RESET_WALKS = pygame.Rect(PAD,                PAD, 140, TOOLBAR_H - 2*PAD)
BTN_RESET       = pygame.Rect(2*PAD + 140,        PAD, 90,  TOOLBAR_H - 2*PAD)
BTN_ADD         = pygame.Rect(3*PAD + 230,        PAD, 160, TOOLBAR_H - 2*PAD)
BTN_TOGGLE_VIEW = pygame.Rect(4*PAD + 390,        PAD, 160, TOOLBAR_H - 2*PAD)
BTN_HOME        = pygame.Rect(WIDTH - PAD - 80,   PAD, 80,  TOOLBAR_H - 2*PAD)


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


def walk1d():
    return 1 if bool(random.getrandbits(1)) else -1


def walk2d():
    return [(1, 0), (-1, 0), (0, 1), (0, -1)][random.randint(0, 3)]


def draw_button(surface, rect, text, hover=False):
    bg = (170, 170, 170) if hover else (210, 210, 210)
    pygame.draw.rect(surface, bg, rect, border_radius=4)
    pygame.draw.rect(surface, AXIS_COLOR, rect, 1, border_radius=4)
    FONT.render_to(surface, (rect.x + 8, rect.y + 6), text, AXIS_COLOR, size=16)


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


def draw_heatmap(surface, counts, color, panel, label, show_legend=True, **_):
    gr = graph_rect(panel)
    pygame.draw.rect(surface, (240, 240, 240), gr)

    if counts:
        xs = [k[0] for k in counts]
        ys = [k[1] for k in counts]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        max_count = max(counts.values())

        cell_w = gr.width  / (span_x + 1)
        cell_h = gr.height / (span_y + 1)

        for (px, py), count in counts.items():
            t = count / max_count
            r = int(color[0] * t + 240 * (1 - t))
            g = int(color[1] * t + 240 * (1 - t))
            b = int(color[2] * t + 240 * (1 - t))
            cx = gr.left + int((px - min_x) / (span_x + 1) * gr.width)
            cy = gr.top  + int((max_y - py) / (span_y + 1) * gr.height)
            pygame.draw.rect(surface, (r, g, b),
                             (cx, cy, max(1, int(cell_w) + 1), max(1, int(cell_h) + 1)))

        for i in range(min(5, span_x + 1)):
            val = min_x + int(i * span_x / max(min(5, span_x + 1) - 1, 1))
            lx  = gr.left + int((val - min_x) / (span_x + 1) * gr.width)
            FONT.render_to(surface, (lx - 6, gr.bottom + 3), str(val), AXIS_COLOR, size=11)

        if show_legend:
            for i in range(min(5, span_y + 1)):
                val = min_y + int(i * span_y / max(min(5, span_y + 1) - 1, 1))
                ly  = gr.top + int((max_y - val) / (span_y + 1) * gr.height)
                FONT.render_to(surface, (panel.left + 1, ly - 5), str(val), AXIS_COLOR, size=11)

    pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.top),    (gr.left,  gr.bottom), 2)
    pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.bottom), (gr.right, gr.bottom), 2)
    FONT.render_to(surface, (gr.left + 2, panel.top + 2), label, color, size=13)


# ── Gaussian blur (separable) ─────────────────────────────────────────────────

def _gaussian_blur_2d(grid, gw, gh, sigma):
    ksize = max(3, int(sigma * 4) | 1)
    k     = ksize // 2
    ws    = [math.exp(-x * x / (2 * sigma * sigma)) for x in range(-k, k + 1)]
    total = sum(ws)
    ws    = [w / total for w in ws]

    tmp = [[0.0] * gh for _ in range(gw)]
    for i in range(gw):
        for j in range(gh):
            v = 0.0
            for ki, w in enumerate(ws):
                jj = j + ki - k
                if 0 <= jj < gh:
                    v += grid[i][jj] * w
            tmp[i][j] = v

    out = [[0.0] * gh for _ in range(gw)]
    for i in range(gw):
        for j in range(gh):
            v = 0.0
            for ki, w in enumerate(ws):
                ii = i + ki - k
                if 0 <= ii < gw:
                    v += tmp[ii][j] * w
            out[i][j] = v
    return out


# Blur result cache: {cache_key: (frame_no, smoothed_grid)}
_gauss_cache: dict = {}
_frame_no: int = 0
_BLUR_INTERVAL = 4   # recompute every N frames


# ── 3-D Gaussian surface ──────────────────────────────────────────────────────

def draw_3d_gaussian(surface, counts, color, panel, label,
                     rotation=math.pi / 4, cache_key=None, **_):
    global _frame_no
    gr = graph_rect(panel)
    pygame.draw.rect(surface, (215, 225, 235), gr)

    def finish():
        pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.top),    (gr.left,  gr.bottom), 2)
        pygame.draw.line(surface, AXIS_COLOR, (gr.left, gr.bottom), (gr.right, gr.bottom), 2)
        FONT.render_to(surface, (gr.left + 2, panel.top + 2), label, color, size=13)

    if not counts:
        finish()
        return

    xs = [k[0] for k in counts]
    ys = [k[1] for k in counts]
    cx_data = (min(xs) + max(xs)) // 2
    cy_data = (min(ys) + max(ys)) // 2

    MAX_HALF = min(20, max(5, gr.width // 16))
    gx0, gx1 = cx_data - MAX_HALF, cx_data + MAX_HALF
    gy0, gy1 = cy_data - MAX_HALF, cy_data + MAX_HALF
    gw = gx1 - gx0 + 1
    gh = gy1 - gy0 + 1

    raw = [[0.0] * gh for _ in range(gw)]
    for (px, py), cnt in counts.items():
        if gx0 <= px <= gx1 and gy0 <= py <= gy1:
            raw[px - gx0][py - gy0] = float(cnt)

    # Cached Gaussian smoothing
    cached = _gauss_cache.get(cache_key)
    if cached is None or (_frame_no - cached[0]) >= _BLUR_INTERVAL:
        smoothed = _gaussian_blur_2d(raw, gw, gh, sigma=1.5)
        if cache_key is not None:
            _gauss_cache[cache_key] = (_frame_no, smoothed)
    else:
        smoothed = cached[1]

    max_val = max(smoothed[i][j] for i in range(gw) for j in range(gh))
    if max_val <= 0:
        finish()
        return

    # ── Projection ────────────────────────────────────────────────────────────
    cos_t = math.cos(rotation)
    sin_t = math.sin(rotation)

    # tile_w sized so grid fits inside panel for any rotation angle
    diag   = math.sqrt(gw * gw + gh * gh)
    tile_w = max(1.0, min(gr.width / diag, 1.2 * gr.height / diag))
    tile_h = tile_w * 0.5
    z_scale = gr.height * 0.40

    def raw_xy(ix, iy, z_norm):
        rx = ix * cos_t - iy * sin_t
        ry = ix * sin_t + iy * cos_t
        return rx * tile_w, ry * tile_h - z_norm * z_scale

    # Centre the base footprint horizontally; anchor bottom edge near gr.bottom
    corners_raw = [raw_xy(ix, iy, 0) for ix, iy in [(0,0),(gw,0),(gw,gh),(0,gh)]]
    min_rx = min(p[0] for p in corners_raw)
    max_rx = max(p[0] for p in corners_raw)
    max_ry = max(p[1] for p in corners_raw)

    off_x = gr.centerx - (min_rx + max_rx) / 2
    off_y = (gr.bottom - 5) - max_ry

    def proj(ix, iy, z_norm):
        rx, ry = raw_xy(ix, iy, z_norm)
        return (int(rx + off_x), int(ry + off_y))

    # ── Face visibility (derived analytically) ────────────────────────────────
    # ix+1 face: visible when sin_t > 0
    # iy+1 face: visible when cos_t > 0
    # ix   face: visible when sin_t < 0
    # iy   face: visible when cos_t < 0
    draw_ix1 = sin_t > 0
    draw_iy1 = cos_t > 0
    draw_ix0 = sin_t < 0
    draw_iy0 = cos_t < 0

    # ── Shading ───────────────────────────────────────────────────────────────
    r, gc, b = color
    top_c  = (min(255, r + 80), min(255, gc + 80), min(255, b + 80))
    ix_c   = color                                                       # ix-direction face
    iy_c   = (max(0, r - 50),   max(0, gc - 50),   max(0, b - 50))     # iy-direction face

    # ── Collect & depth-sort cells ────────────────────────────────────────────
    cells = [
        (i, j, smoothed[i][j] / max_val)
        for i in range(gw) for j in range(gh)
        if smoothed[i][j] / max_val > 0.015
    ]
    # depth = ry component = ix*sin_t + iy*cos_t; draw min-depth first (back-to-front)
    cells.sort(key=lambda c: c[0] * sin_t + c[1] * cos_t)

    surface.set_clip(gr)

    for ix, iy, h in cells:
        p00 = proj(ix,   iy,   0)
        p10 = proj(ix+1, iy,   0)
        p11 = proj(ix+1, iy+1, 0)
        p01 = proj(ix,   iy+1, 0)
        t00 = proj(ix,   iy,   h)
        t10 = proj(ix+1, iy,   h)
        t11 = proj(ix+1, iy+1, h)
        t01 = proj(ix,   iy+1, h)

        if h > 0.03:
            if draw_ix1:
                pygame.draw.polygon(surface, ix_c,  [p10, p11, t11, t10])
            if draw_iy1:
                pygame.draw.polygon(surface, iy_c,  [p11, p01, t01, t11])
            if draw_ix0:
                pygame.draw.polygon(surface, ix_c,  [p01, p00, t00, t01])
            if draw_iy0:
                pygame.draw.polygon(surface, iy_c,  [p00, p10, t10, t00])

        pygame.draw.polygon(surface, top_c, [t00, t10, t11, t01])

    # ── X / Y axis arrows at the grid base ───────────────────────────────────
    arm   = max(3, MAX_HALF // 3)
    mid_i = gw // 2
    mid_j = gh // 2
    o_pt  = proj(mid_i,       mid_j,       0)
    x_pt  = proj(mid_i + arm, mid_j,       0)
    y_pt  = proj(mid_i,       mid_j + arm, 0)
    pygame.draw.line(surface, (210, 50,  50),  o_pt, x_pt, 2)
    pygame.draw.line(surface, (50,  170, 50),  o_pt, y_pt, 2)
    FONT.render_to(surface, (x_pt[0] + 2, x_pt[1] - 6), "X", (210, 50,  50),  size=11)
    FONT.render_to(surface, (y_pt[0] + 2, y_pt[1] - 6), "Y", (50,  170, 50),  size=11)

    surface.set_clip(None)
    finish()


# ── Mode selection ────────────────────────────────────────────────────────────

def choose_mode():
    BTN_1D = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 40, 140, 80)
    BTN_2D = pygame.Rect(WIDTH // 2 +  20, HEIGHT // 2 - 40, 140, 80)
    clock  = pygame.time.Clock()

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    raise SystemExit
                elif event.key == pygame.K_1:
                    return "1d"
                elif event.key == pygame.K_2:
                    return "2d"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if BTN_1D.collidepoint(mx, my):
                    return "1d"
                if BTN_2D.collidepoint(mx, my):
                    return "2d"

        screen.fill((255, 255, 255))
        FONT.render_to(screen, (WIDTH // 2 - 120, HEIGHT // 2 - 90),
                       "Choose simulation mode", AXIS_COLOR, size=24)
        h1 = BTN_1D.collidepoint(mx, my)
        h2 = BTN_2D.collidepoint(mx, my)
        pygame.draw.rect(screen, (170, 170, 170) if h1 else (210, 210, 210), BTN_1D, border_radius=8)
        pygame.draw.rect(screen, AXIS_COLOR, BTN_1D, 2, border_radius=8)
        FONT.render_to(screen, (BTN_1D.x + 38, BTN_1D.y + 24), "1D", PALETTE[0], size=28)
        pygame.draw.rect(screen, (170, 170, 170) if h2 else (210, 210, 210), BTN_2D, border_radius=8)
        pygame.draw.rect(screen, AXIS_COLOR, BTN_2D, 2, border_radius=8)
        FONT.render_to(screen, (BTN_2D.x + 38, BTN_2D.y + 24), "2D", PALETTE[1], size=28)
        pygame.display.update()
        clock.tick(60)


clock = pygame.time.Clock()

while True:
    mode = choose_mode()

    # ── 1-D simulation ────────────────────────────────────────────────────────

    if mode == "1d":
        positions = [0] * 4
        counts    = [defaultdict(int) for _ in range(4)]
        loop      = True

        while loop:
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        raise SystemExit
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if BTN_HOME.collidepoint(mx, my):
                        loop = False
                    elif BTN_RESET_WALKS.collidepoint(mx, my):
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
                positions[i] += walk1d()
                counts[i][positions[i]] += 1

            all_keys   = set().union(*counts)
            sum_counts = {x: sum(c.get(x, 0) for c in counts) for x in all_keys}
            panels     = side_panels(n)

            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, (225, 225, 225), (0, 0, WIDTH, TOOLBAR_H))
            draw_button(screen, BTN_RESET_WALKS, "Reset Walks", BTN_RESET_WALKS.collidepoint(mx, my))
            draw_button(screen, BTN_RESET,       "Reset",        BTN_RESET.collidepoint(mx, my))
            draw_button(screen, BTN_ADD,         "+ Add Walker", BTN_ADD.collidepoint(mx, my))
            draw_button(screen, BTN_HOME,        "Home",         BTN_HOME.collidepoint(mx, my))

            for i in range(n):
                draw_histogram(screen, counts[i], PALETTE[i % len(PALETTE)], panels[i],
                               f"W{i+1} X={positions[i]}", show_y_axis=False)
            draw_histogram(screen, sum_counts, SUM_COLOR, CENTER_PANEL, "Sum", show_y_axis=True)

            pygame.display.update()
            clock.tick(FPS)

    # ── 2-D simulation ────────────────────────────────────────────────────────

    else:
        view_mode = "heatmap"
        positions = [(0, 0)] * 4
        counts    = [defaultdict(int) for _ in range(4)]
        rotations: dict = {}
        drag_info = None
        _gauss_cache.clear()
        loop      = True

        while loop:
            mx, my = pygame.mouse.get_pos()
            n      = len(positions)
            panels = side_panels(n)
            panel_map = [(panels[i], i) for i in range(n)] + [(CENTER_PANEL, 'sum')]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        raise SystemExit
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    emx, emy = event.pos
                    if BTN_HOME.collidepoint(emx, emy):
                        loop = False
                    elif BTN_RESET_WALKS.collidepoint(emx, emy):
                        positions = [(0, 0)] * len(positions)
                        counts    = [defaultdict(int) for _ in range(len(positions))]
                        _gauss_cache.clear()
                    elif BTN_RESET.collidepoint(emx, emy):
                        positions = [(0, 0)] * 4
                        counts    = [defaultdict(int) for _ in range(4)]
                        _gauss_cache.clear()
                    elif BTN_ADD.collidepoint(emx, emy):
                        positions.append((0, 0))
                        counts.append(defaultdict(int))
                    elif BTN_TOGGLE_VIEW.collidepoint(emx, emy):
                        view_mode = "3d" if view_mode == "heatmap" else "heatmap"
                    elif view_mode == "3d":
                        for rect, key in panel_map:
                            if rect.collidepoint(emx, emy):
                                drag_info = {
                                    'key':         key,
                                    'start_mx':    emx,
                                    'start_angle': rotations.get(key, math.pi / 4),
                                }
                                break
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    drag_info = None
                elif event.type == pygame.MOUSEMOTION:
                    if drag_info is not None:
                        dx = event.pos[0] - drag_info['start_mx']
                        rotations[drag_info['key']] = drag_info['start_angle'] + dx * 0.01

            n = len(positions)
            for i in range(n):
                dx, dy = walk2d()
                positions[i] = (positions[i][0] + dx, positions[i][1] + dy)
                counts[i][positions[i]] += 1

            all_keys   = set().union(*counts)
            sum_counts = {k: sum(c.get(k, 0) for c in counts) for k in all_keys}
            panels     = side_panels(n)
            btn_view_label = "View: Heatmap" if view_mode == "heatmap" else "View: 3D Gauss"

            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, (225, 225, 225), (0, 0, WIDTH, TOOLBAR_H))
            draw_button(screen, BTN_RESET_WALKS, "Reset Walks",  BTN_RESET_WALKS.collidepoint(mx, my))
            draw_button(screen, BTN_RESET,       "Reset",         BTN_RESET.collidepoint(mx, my))
            draw_button(screen, BTN_ADD,         "+ Add Walker",  BTN_ADD.collidepoint(mx, my))
            draw_button(screen, BTN_TOGGLE_VIEW, btn_view_label,  BTN_TOGGLE_VIEW.collidepoint(mx, my))
            draw_button(screen, BTN_HOME,        "Home",          BTN_HOME.collidepoint(mx, my))

            if view_mode == "heatmap":
                for i in range(n):
                    px, py = positions[i]
                    draw_heatmap(screen, counts[i], PALETTE[i % len(PALETTE)], panels[i],
                                 f"W{i+1} ({px},{py})", show_legend=False)
                draw_heatmap(screen, sum_counts, SUM_COLOR, CENTER_PANEL, "Sum", show_legend=True)
            else:
                for i in range(n):
                    px, py = positions[i]
                    draw_3d_gaussian(screen, counts[i], PALETTE[i % len(PALETTE)], panels[i],
                                     f"W{i+1} ({px},{py})",
                                     rotation=rotations.get(i, math.pi / 4),
                                     cache_key=i)
                draw_3d_gaussian(screen, sum_counts, SUM_COLOR, CENTER_PANEL, "Sum",
                                 rotation=rotations.get('sum', math.pi / 4),
                                 cache_key='sum')
                _frame_no += 1

            pygame.display.update()
            clock.tick(FPS)
