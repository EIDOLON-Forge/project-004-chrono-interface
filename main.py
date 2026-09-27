import pygame
import random
import math
import wave
import struct
from datetime import datetime


# ============================================================
# EIDOLON — PROJECT #004
# CHRONO INTERFACE
# ============================================================

WIDTH = 1000
HEIGHT = 650
FPS = 60

# Main visual center
CENTER = (WIDTH // 2, 325)

BACKGROUND = (3, 6, 7)
GRID_COLOR = (8, 25, 25)

PARTICLE_COUNT = 100
SAMPLE_RATE = 44100


# ============================================================
# THEMES
# ============================================================

THEMES = [
    {
        "name": "EIDOLON",
        "primary": (205, 235, 220),
        "secondary": (95, 155, 125),
        "accent": (120, 205, 155),
    },
    {
        "name": "ICE",
        "primary": (215, 235, 255),
        "secondary": (100, 155, 205),
        "accent": (130, 205, 255),
    },
    {
        "name": "AMBER",
        "primary": (245, 225, 180),
        "secondary": (180, 135, 75),
        "accent": (235, 175, 75),
    },
]


# ============================================================
# AUDIO
# ============================================================

def create_tone(
    filename,
    start_frequency,
    end_frequency,
    duration,
    volume
):
    samples = int(SAMPLE_RATE * duration)

    with wave.open(filename, "w") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        data = bytearray()

        for i in range(samples):

            t = i / SAMPLE_RATE
            progress = i / max(1, samples - 1)

            frequency = (
                start_frequency
                + (
                    end_frequency
                    - start_frequency
                )
                * progress
            )

            envelope = 1.0

            fade_in = 0.015
            fade_out = 0.04

            if t < fade_in:
                envelope *= t / fade_in

            if t > duration - fade_out:
                envelope *= (
                    duration - t
                ) / fade_out

            value = math.sin(
                2 * math.pi * frequency * t
            )

            value += 0.25 * math.sin(
                2 * math.pi * frequency * 2 * t
            )

            sample = int(
                32767
                * value
                * volume
                * envelope
            )

            sample = max(
                -32767,
                min(32767, sample)
            )

            data.extend(
                struct.pack("<h", sample)
            )

        wav.writeframes(data)


# ============================================================
# PYGAME INITIALIZATION
# ============================================================

pygame.init()

try:

    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=1,
        buffer=512
    )

    AUDIO_AVAILABLE = True

except pygame.error:

    AUDIO_AVAILABLE = False


screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "EIDOLON — Project #004: Chrono Interface"
)

clock = pygame.time.Clock()


# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.Font(
    None,
    20
)

FONT_MEDIUM = pygame.font.Font(
    None,
    27
)

FONT_LARGE = pygame.font.Font(
    None,
    36
)

FONT_TITLE = pygame.font.Font(
    None,
    62
)

FONT_COUNTDOWN = pygame.font.Font(
    None,
    150
)

CLOCK_FONT = pygame.font.Font(
    None,
    145
)


# ============================================================
# CREATE AUDIO
# ============================================================

if AUDIO_AVAILABLE:

    create_tone(
        "tick.wav",
        900,
        650,
        0.035,
        0.22
    )

    create_tone(
        "start.wav",
        280,
        900,
        0.35,
        0.45
    )

    create_tone(
        "countdown.wav",
        520,
        360,
        0.14,
        0.35
    )

    tick_sound = pygame.mixer.Sound(
        "tick.wav"
    )

    start_sound = pygame.mixer.Sound(
        "start.wav"
    )

    countdown_sound = pygame.mixer.Sound(
        "countdown.wav"
    )

    tick_sound.set_volume(0.18)
    start_sound.set_volume(0.45)
    countdown_sound.set_volume(0.35)

else:

    tick_sound = None
    start_sound = None
    countdown_sound = None


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(self):
        self.reset()

    def reset(self):

        self.x = random.uniform(
            0,
            WIDTH
        )

        self.y = random.uniform(
            0,
            HEIGHT
        )

        self.speed = random.uniform(
            0.08,
            0.35
        )

        self.size = random.choice(
            [1, 1, 1, 2]
        )

        self.alpha = random.randint(
            25,
            90
        )

        self.phase = random.uniform(
            0,
            math.tau
        )

    def update(self):

        self.y -= self.speed

        self.phase += 0.015

        if self.y < -5:

            self.y = HEIGHT + 5

            self.x = random.uniform(
                0,
                WIDTH
            )

    def draw(
        self,
        surface,
        color
    ):

        pulse = (
            math.sin(self.phase) + 1
        ) / 2

        alpha = int(
            self.alpha
            * (
                0.55
                + pulse * 0.45
            )
        )

        size = self.size * 4

        particle_surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (
                color[0],
                color[1],
                color[2],
                alpha
            ),
            (
                size // 2,
                size // 2
            ),
            self.size
        )

        surface.blit(
            particle_surface,
            (
                int(self.x - size / 2),
                int(self.y - size / 2)
            )
        )


particles = [
    Particle()
    for _ in range(PARTICLE_COUNT)
]


# ============================================================
# TEXT HELPER
# ============================================================

def draw_centered_text(
    surface,
    text,
    font,
    color,
    position
):

    rendered = font.render(
        text,
        True,
        color
    )

    rect = rendered.get_rect(
        center=position
    )

    surface.blit(
        rendered,
        rect
    )


# ============================================================
# GRID
# ============================================================

def draw_grid(surface):

    spacing = 62

    for x in range(
        0,
        WIDTH,
        spacing
    ):

        pygame.draw.line(
            surface,
            GRID_COLOR,
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(
        0,
        HEIGHT,
        spacing
    ):

        pygame.draw.line(
            surface,
            GRID_COLOR,
            (0, y),
            (WIDTH, y),
            1
        )


# ============================================================
# CORNER BRACKETS
# ============================================================

def draw_corner_brackets(
    surface,
    color
):

    margin = 125
    length = 32

    corners = [
        (
            margin,
            margin,
            1,
            1
        ),
        (
            WIDTH - margin,
            margin,
            -1,
            1
        ),
        (
            margin,
            HEIGHT - margin,
            1,
            -1
        ),
        (
            WIDTH - margin,
            HEIGHT - margin,
            -1,
            -1
        ),
    ]

    for x, y, dx, dy in corners:

        pygame.draw.line(
            surface,
            color,
            (x, y),
            (
                x + dx * length,
                y
            ),
            3
        )

        pygame.draw.line(
            surface,
            color,
            (x, y),
            (
                x,
                y + dy * length
            ),
            3
        )


# ============================================================
# SECONDS RING
# ============================================================

def draw_seconds_ring(
    surface,
    center,
    seconds,
    secondary,
    accent
):

    cx, cy = center

    outer_radius = 245
    inner_radius = 231

    # --------------------------------------------------------
    # Outer rings
    # --------------------------------------------------------

    pygame.draw.circle(
        surface,
        (
            secondary[0] // 4,
            secondary[1] // 4,
            secondary[2] // 4
        ),
        center,
        outer_radius,
        1
    )

    pygame.draw.circle(
        surface,
        (
            secondary[0] // 3,
            secondary[1] // 3,
            secondary[2] // 3
        ),
        center,
        inner_radius,
        1
    )

    # --------------------------------------------------------
    # 60 tick marks
    # --------------------------------------------------------

    for i in range(60):

        angle = math.radians(
            i * 6 - 90
        )

        if i % 5 == 0:

            tick_length = 14
            tick_width = 2

        else:

            tick_length = 7
            tick_width = 1

        r1 = outer_radius - 3
        r2 = r1 - tick_length

        x1 = (
            cx
            + math.cos(angle) * r1
        )

        y1 = (
            cy
            + math.sin(angle) * r1
        )

        x2 = (
            cx
            + math.cos(angle) * r2
        )

        y2 = (
            cy
            + math.sin(angle) * r2
        )

        pygame.draw.line(
            surface,
            secondary,
            (
                int(x1),
                int(y1)
            ),
            (
                int(x2),
                int(y2)
            ),
            tick_width
        )

    # --------------------------------------------------------
    # Progress arc
    # --------------------------------------------------------

    progress = seconds / 60.0

    start_angle = -math.pi / 2

    end_angle = (
        start_angle
        + math.tau * progress
    )

    arc_rect = pygame.Rect(
        cx - outer_radius,
        cy - outer_radius,
        outer_radius * 2,
        outer_radius * 2
    )

    # Subtle glow
    for width, alpha in [
        (8, 15),
        (5, 25),
        (3, 40),
    ]:

        glow_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        pygame.draw.arc(
            glow_surface,
            (
                accent[0],
                accent[1],
                accent[2],
                alpha
            ),
            arc_rect,
            start_angle,
            end_angle,
            width
        )

        surface.blit(
            glow_surface,
            (0, 0)
        )

    # Main arc
    pygame.draw.arc(
        surface,
        accent,
        arc_rect,
        start_angle,
        end_angle,
        4
    )


# ============================================================
# CLOCK
# ============================================================

def draw_clock(
    surface,
    center,
    time_text,
    primary,
    accent
):

    cx, cy = center

    # --------------------------------------------------------
    # Render clock text
    # --------------------------------------------------------

    text_surface = CLOCK_FONT.render(
        time_text,
        True,
        primary
    )

    text_rect = text_surface.get_rect(
        center=(cx, cy)
    )

    # --------------------------------------------------------
    # Dark glass backing
    # --------------------------------------------------------

    panel_padding_x = 34
    panel_padding_y = 21

    panel_rect = pygame.Rect(
        text_rect.left
        - panel_padding_x,

        text_rect.top
        - panel_padding_y,

        text_rect.width
        + panel_padding_x * 2,

        text_rect.height
        + panel_padding_y * 2
    )

    # --------------------------------------------------------
    # Very subtle panel glow
    # --------------------------------------------------------

    for expand, alpha in [
        (16, 10),
        (10, 16),
        (5, 22),
    ]:

        glow_rect = panel_rect.inflate(
            expand * 2,
            expand * 2
        )

        glow_surface = pygame.Surface(
            glow_rect.size,
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            glow_surface,
            (
                accent[0],
                accent[1],
                accent[2],
                alpha
            ),
            glow_surface.get_rect(),
            border_radius=16
        )

        surface.blit(
            glow_surface,
            glow_rect.topleft
        )

    # --------------------------------------------------------
    # Main opaque panel
    # --------------------------------------------------------

    panel = pygame.Surface(
        panel_rect.size,
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        panel,
        (
            2,
            6,
            6,
            245
        ),
        panel.get_rect(),
        border_radius=15
    )

    # Thin accent border
    pygame.draw.rect(
        panel,
        (
            accent[0],
            accent[1],
            accent[2],
            38
        ),
        panel.get_rect(),
        width=1,
        border_radius=15
    )

    surface.blit(
        panel,
        panel_rect.topleft
    )

    # --------------------------------------------------------
    # Extremely subtle glow
    # --------------------------------------------------------

    glow_text = CLOCK_FONT.render(
        time_text,
        True,
        accent
    )

    for dx, dy, alpha in [
        (-2, 0, 12),
        (2, 0, 12),
        (0, -2, 8),
        (0, 2, 8),
    ]:

        glow_copy = glow_text.copy()

        glow_copy.set_alpha(
            alpha
        )

        surface.blit(
            glow_copy,
            (
                text_rect.x + dx,
                text_rect.y + dy
            )
        )

    # --------------------------------------------------------
    # CRISP MAIN DIGITS
    # --------------------------------------------------------

    surface.blit(
        text_surface,
        text_rect
    )


# ============================================================
# STATUS BAR
# ============================================================

def draw_status(
    surface,
    secondary,
    accent,
    muted
):

    status_y = 610

    statuses = [
        (
            "SYNC",
            accent
        ),
        (
            "CLOCK",
            accent
        ),
        (
            "AUDIO",
            secondary if muted else accent
        ),
    ]

    positions = [
        175,
        WIDTH // 2,
        WIDTH - 175
    ]

    for (label, color), x in zip(
        statuses,
        positions
    ):

        pygame.draw.circle(
            surface,
            color,
            (
                x - 45,
                status_y
            ),
            5
        )

        text = FONT_MEDIUM.render(
            label,
            True,
            color
        )

        text_rect = text.get_rect(
            midleft=(
                x - 30,
                status_y
            )
        )

        surface.blit(
            text,
            text_rect
        )


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(
    surface,
    theme
):

    primary = theme["primary"]
    secondary = theme["secondary"]
    accent = theme["accent"]

    surface.fill(
        BACKGROUND
    )

    draw_grid(
        surface
    )

    for particle in particles:

        particle.update()

        particle.draw(
            surface,
            secondary
        )

    draw_corner_brackets(
        surface,
        secondary
    )

    draw_centered_text(
        surface,
        "CHRONO",
        FONT_TITLE,
        primary,
        (
            WIDTH // 2,
            270
        )
    )

    draw_centered_text(
        surface,
        "INTERFACE",
        FONT_LARGE,
        accent,
        (
            WIDTH // 2,
            325
        )
    )

    draw_centered_text(
        surface,
        "PRESS SPACE TO INITIALIZE",
        FONT_MEDIUM,
        secondary,
        (
            WIDTH // 2,
            390
        )
    )

    draw_centered_text(
        surface,
        "EIDOLON // PROJECT 004",
        FONT_SMALL,
        secondary,
        (
            WIDTH // 2,
            580
        )
    )


# ============================================================
# COUNTDOWN
# ============================================================

def run_countdown(
    surface,
    theme
):

    primary = theme["primary"]
    secondary = theme["secondary"]

    for number in [
        "3",
        "2",
        "1"
    ]:

        if AUDIO_AVAILABLE:
            countdown_sound.play()

        start_time = (
            pygame.time.get_ticks()
        )

        while (
            pygame.time.get_ticks()
            - start_time
            < 700
        ):

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()
                    raise SystemExit

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):

                    pygame.quit()
                    raise SystemExit

            surface.fill(
                BACKGROUND
            )

            draw_grid(
                surface
            )

            for particle in particles:

                particle.update()

                particle.draw(
                    surface,
                    secondary
                )

            draw_centered_text(
                surface,
                number,
                FONT_COUNTDOWN,
                primary,
                CENTER
            )

            pygame.display.flip()

            clock.tick(FPS)

    if AUDIO_AVAILABLE:
        start_sound.play()

    start_time = (
        pygame.time.get_ticks()
    )

    while (
        pygame.time.get_ticks()
        - start_time
        < 800
    ):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                raise SystemExit

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):

                pygame.quit()
                raise SystemExit

        surface.fill(
            BACKGROUND
        )

        draw_grid(
            surface
        )

        draw_centered_text(
            surface,
            "GO",
            FONT_COUNTDOWN,
            primary,
            CENTER
        )

        pygame.display.flip()

        clock.tick(FPS)


# ============================================================
# MAIN
# ============================================================

def main():

    theme_index = 0

    use_24_hour = True
    show_seconds = True
    show_date = True

    muted = False
    paused = False

    initialized = False
    running = True

    last_second = -1

    # --------------------------------------------------------
    # START SCREEN
    # --------------------------------------------------------

    while not initialized:

        theme = THEMES[
            theme_index
        ]

        draw_start_screen(
            screen,
            theme
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    pygame.quit()
                    return

                if event.key == pygame.K_SPACE:

                    run_countdown(
                        screen,
                        theme
                    )

                    initialized = True
                    break

        clock.tick(FPS)

    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    while running:

        theme = THEMES[
            theme_index
        ]

        primary = theme["primary"]
        secondary = theme["secondary"]
        accent = theme["accent"]

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.KEYDOWN:

                # Pause
                if event.key == pygame.K_SPACE:

                    paused = not paused

                # Audio
                elif event.key == pygame.K_m:

                    muted = not muted

                    if AUDIO_AVAILABLE:

                        if muted:
                            pygame.mixer.pause()
                        else:
                            pygame.mixer.unpause()

                # Date
                elif event.key == pygame.K_d:

                    show_date = not show_date

                # Theme
                elif event.key == pygame.K_c:

                    theme_index = (
                        theme_index + 1
                    ) % len(THEMES)

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_x, mouse_y = (
                        pygame.mouse.get_pos()
                    )

                    distance = math.sqrt(
                        (
                            mouse_x
                            - CENTER[0]
                        ) ** 2
                        +
                        (
                            mouse_y
                            - CENTER[1]
                        ) ** 2
                    )

                    # Toggle 12/24 hour
                    if distance < 150:

                        use_24_hour = (
                            not use_24_hour
                        )

                    # Toggle seconds
                    elif (
                        195
                        <= distance
                        <= 250
                    ):

                        show_seconds = (
                            not show_seconds
                        )

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

        # ====================================================
        # UPDATE
        # ====================================================

        if not paused:

            for particle in particles:

                particle.update()

        # ====================================================
        # CURRENT TIME
        # ====================================================

        now = datetime.now()

        if use_24_hour:

            hour_text = now.strftime(
                "%H"
            )

        else:

            hour_text = now.strftime(
                "%I"
            )

        minute_text = now.strftime(
            "%M"
        )

        second_text = now.strftime(
            "%S"
        )

        if show_seconds:

            time_text = (
                f"{hour_text}:"
                f"{minute_text}:"
                f"{second_text}"
            )

        else:

            time_text = (
                f"{hour_text}:"
                f"{minute_text}"
            )

        # ====================================================
        # TICK
        # ====================================================

        if (
            now.second != last_second
            and not muted
        ):

            if AUDIO_AVAILABLE:

                tick_sound.play()

            last_second = now.second

        # ====================================================
        # DRAW BACKGROUND
        # ====================================================

        screen.fill(
            BACKGROUND
        )

        draw_grid(
            screen
        )

        # ====================================================
        # PARTICLES
        # ====================================================

        for particle in particles:

            particle.draw(
                screen,
                secondary
            )

        # ====================================================
        # MOUSE PARALLAX
        # ====================================================

        mouse_x, mouse_y = (
            pygame.mouse.get_pos()
        )

        parallax_x = int(
            (
                mouse_x
                - WIDTH / 2
            ) * 0.006
        )

        parallax_y = int(
            (
                mouse_y
                - HEIGHT / 2
            ) * 0.006
        )

        # ====================================================
        # HEADER
        # ====================================================

        header_y = 145

        header_left = FONT_LARGE.render(
            "EIDOLON",
            True,
            primary
        )

        header_left_rect = (
            header_left.get_rect(
                midleft=(
                    155 + parallax_x,
                    header_y + parallax_y
                )
            )
        )

        screen.blit(
            header_left,
            header_left_rect
        )

        header_right = FONT_MEDIUM.render(
            f"MODE // {theme['name']}",
            True,
            secondary
        )

        header_right_rect = (
            header_right.get_rect(
                midright=(
                    WIDTH - 155 + parallax_x,
                    header_y + parallax_y
                )
            )
        )

        screen.blit(
            header_right,
            header_right_rect
        )

        # ====================================================
        # CORNER BRACKETS
        # ====================================================

        draw_corner_brackets(
            screen,
            secondary
        )

        # ====================================================
        # SECONDS RING
        # ====================================================

        visual_center = (
            CENTER[0] + parallax_x,
            CENTER[1] + parallax_y
        )

        draw_seconds_ring(
            screen,
            visual_center,
            now.second,
            secondary,
            accent
        )

        # ====================================================
        # MAIN CLOCK
        # ====================================================

        draw_clock(
            screen,
            visual_center,
            time_text,
            primary,
            accent
        )

        # ====================================================
        # DATE
        # ====================================================

        if show_date:

            date_text = now.strftime(
                "%A • %d %B %Y"
            )

            draw_centered_text(
                screen,
                date_text.upper(),
                FONT_LARGE,
                secondary,
                (
                    CENTER[0] + parallax_x,
                    CENTER[1]
                    + 110
                    + parallax_y
                )
            )

        # ====================================================
        # PAUSED INDICATOR
        # ====================================================

        if paused:

            draw_centered_text(
                screen,
                "VISUAL SYSTEM PAUSED",
                FONT_SMALL,
                accent,
                (
                    WIDTH // 2,
                    485
                )
            )

        # ====================================================
        # CONTROL BAR
        # ====================================================

        control_y = 535

        controls = [
            ("SPACE", "PAUSE"),
            ("M", "AUDIO"),
            ("D", "DATE"),
            ("C", "THEME"),
            ("CLICK", "12/24H"),
        ]

        control_positions = [
            205,
            365,
            515,
            665,
            825,
        ]

        for (
            key_label,
            action_label
        ), x in zip(
            controls,
            control_positions
        ):

            key_surface = FONT_SMALL.render(
                key_label,
                True,
                accent
            )

            label_surface = FONT_SMALL.render(
                action_label,
                True,
                secondary
            )

            key_rect = (
                key_surface.get_rect(
                    midright=(
                        x,
                        control_y
                    )
                )
            )

            label_rect = (
                label_surface.get_rect(
                    midleft=(
                        x + 7,
                        control_y
                    )
                )
            )

            screen.blit(
                key_surface,
                key_rect
            )

            screen.blit(
                label_surface,
                label_rect
            )

        # ====================================================
        # STATUS BAR
        # ====================================================

        draw_status(
            screen,
            secondary,
            accent,
            muted
        )

        # ====================================================
        # DISPLAY
        # ====================================================

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()