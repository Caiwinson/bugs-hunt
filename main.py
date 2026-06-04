import os
import sys
import pygame
import math
import random
import threading
import time


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Assets
assets = {
    "butterfly": [],
    "devil-ant": [],
    "dragonfly": [],
    "black": [],
    "red-ant": [],
    "green": [],
    "jump": [],
    "mosquito": [],
    "bee": [],
    "oi-oi-oi": [],
}

# Stats for each bug
bug_stats = {
    "butterfly": {
        "fps": 10,
        "time": (4000, 9000),
        "y-type": "flight",
        "height-range": (100, 400),
        "magnitude-range": (75, 150),
        "frequency-range": (1/3, 2)
    },
    "devil-ant": {
        "fps": 1,
        "time": (700, 1400),
        "y-type": "ground",
        "height-range": 500
    },
    "dragonfly": {
        "fps": 20,
        "time": (2500, 6666),
        "y-type": "flight",
        "height-range": (50, 450),
        "magnitude-range": (50, 75),
        "frequency-range": (1/3, 3)
    },
    "black": {
        "fps": 1,
        "time": (2000, 3000),
        "y-type": "leap",
        "height-range": (0, 200),
        "magnitude-range": (200, 500),
        "frequency-range": (1/2, 1.5)
    },
    "red-ant": {
        "fps": 1,
        "time": (1500, 3000),
        "y-type": "ground",
        "height-range": 500
    },
    "green": {
        "fps": 30,
        "time": (3000, 6666),
        "y-type": "flight",
        "height-range": (50, 450),
        "magnitude-range": (50, 75),
        "frequency-range": (1/3, 3)
    },
    "jump": {
        "fps": 1,
        "time": (2000, 3000),
        "y-type": "leap",
        "height-range": (0, 200),
        "magnitude-range": (200, 500),
        "frequency-range": (1/2, 1.5)
    },
    "mosquito": {
        "fps": 1,
        "time": (4000, 9000),
        "y-type": "flight",
        "height-range": (100, 400),
        "magnitude-range": (75, 150),
        "frequency-range": (1/3, 2)
    },
    "bee": {
        "fps": 40,
        "time": (4000, 9000),
        "y-type": "flight",
        "height-range": (100, 400),
        "magnitude-range": (75, 150),
        "frequency-range": (1/3, 2)
    }
}


def preload():
    # preload bug
    for bug in bug_stats.keys():
        file_list = os.listdir(resource_path(f'bugs/{bug}'))
        file_list = sorted([file for file in file_list if file.endswith(
            '.png')], key=lambda x: int(x.split('.')[0]))
        for frame in file_list:
            image = pygame.image.load(resource_path(f'bugs/{bug}/{frame}'))
            resized_image = pygame.transform.scale(
                image, (100, 100)).convert_alpha()
            assets[bug].append(resized_image)

    # preload audio
    for file in os.listdir(resource_path('audio')):
        if file.endswith('.wav') or file.endswith('.mp3'):
            audio = pygame.mixer.Sound(resource_path(f'audio/{file}'))
            assets[file.split('.')[0]] = audio

    # preload blood
    assets["blood_frame"] = pygame.transform.scale(pygame.image.load(
        resource_path("assets/blood.png")), (100, 100)).convert_alpha()
    assets["loading"] = pygame.image.load(
        resource_path("assets/loading.png")).convert_alpha()
    assets["minigun"] = pygame.image.load(
        resource_path("assets/minigun.png")).convert_alpha()

    for i in range(0, 7):
        gun = pygame.image.load(resource_path(
            f"assets/single{i}.png")).convert_alpha()
        assets[f"single{i}"] = gun
    for i in range(0, 3):
        gun = pygame.image.load(resource_path(
            f"assets/wide{i}.png")).convert_alpha()
        assets[f"wide{i}"] = gun

    # Load oi-oi-oi from spritesheet (20x20 grid, 652x600 per frame, 398 frames total)
    _ss = pygame.image.load(resource_path(
        "oi-oi-oi/spritesheet.png")).convert()
    _cols, _fw, _fh = 20, 652, 600
    for _i in range(398):
        _col = _i % _cols
        _row = _i // _cols
        assets["oi-oi-oi"].append(_ss.subsurface((_col *
                                  _fw, _row * _fh, _fw, _fh)))


class Bug:
    def __init__(self, name):
        self.name = name
        self.time_spawned = pygame.time.get_ticks()
        self.frames = []
        self.flipped_frames = []
        self.time = random.randint(*bug_stats[name]["time"])
        self.load_frames()
        self.flipped = random.choice([True, False])
        self.flight_type = bug_stats[name]["y-type"]
        self.fps = bug_stats[name]["fps"]
        self.destroy = False
        if self.flight_type == "ground":
            self.height = bug_stats[name]["height-range"]
            self.magnitude = 0
            self.frequency = 0
        else:
            self.height = random.randint(*bug_stats[name]["height-range"])
            self.magnitude = random.randint(
                *bug_stats[name]["magnitude-range"])
            self.frequency = random.uniform(
                *bug_stats[name]["frequency-range"])

    def load_frames(self):
        self.frames = assets[self.name]
        # Pre-cache horizontally flipped versions
        self.flipped_frames = [pygame.transform.flip(
            f, True, False).convert_alpha() for f in self.frames]
        self.frame_count = len(self.frames)

    def get_position(self):
        # Calculate the elapsed time
        elapsed_time = pygame.time.get_ticks() - self.time_spawned

        # x, -100->800 in 10 seconds
        x = (elapsed_time / self.time) * 900
        # y, sin wave
        if self.flight_type == "flight":
            y = self.height + self.magnitude * \
                math.sin(elapsed_time / 1000 * self.frequency)
        elif self.flight_type == "ground":
            y = self.height
        elif self.flight_type == "leap":
            angle = (elapsed_time / self.time) * 180 * self.frequency
            if angle > 270:
                angle = 270
            y = 600 - (self.height + self.magnitude *
                       math.sin(math.radians(angle)))

        # Change direction if flipped
        if self.flipped:
            x = 800 - x
            if x <= -100:
                self.destroy = True

        else:
            x = x - 100
            if x >= 800:
                self.destroy = True

        return (int(x), int(y))

    def draw(self, screen):
        fps = self.fps
        c = (pygame.time.get_ticks() -
             self.time_spawned) // (1000 // fps) % self.frame_count
        if self.flipped:
            image = self.flipped_frames[c]
        else:
            image = self.frames[c]
        screen.blit(image, self.get_position())

    def draw_white(self, screen):
        # draw white 100x100 rectangle
        pygame.draw.rect(screen, (255, 255, 255),
                         (self.get_position(), (100, 100)))


class Blood:
    # draw assets["blood"] on screen for 2 seconds, reducing opacity
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_spawned = pygame.time.get_ticks()
        # Convert to per-surface alpha via SRCALPHA to avoid mutating the shared asset
        base = assets["blood_frame"]
        self.frame = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        self.frame.blit(base, (0, 0))
        self.destroy = False

    def draw(self, screen):
        elapsed_time = pygame.time.get_ticks() - self.time_spawned
        if elapsed_time > 2000:
            self.destroy = True
            return
        alpha = int(255 * (1 - elapsed_time / 2000))
        self.frame.set_alpha(alpha)
        screen.blit(self.frame, (self.x, self.y))


# Initialize Pygame
pygame.init()

# Initialize the mixer module
pygame.mixer.init()
pygame.mixer.set_num_channels(3)

# Initialize the font module
pygame.font.init()

# Create a font object
font = pygame.font.Font(None, 36)  # You can specify the font file and size

# Set up the display, borderless window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Bug Game")
pygame.mouse.set_visible(False)

preload()

max_fps = 60

# Load background image
background = pygame.image.load(resource_path('background.png')).convert()

game_data = {
    "score": 0,
    "bugs": [],
    "blood": []
}
game_data_lock = threading.Lock()

flash_banged = 0
flashbang_type = 0

display_mode = False

# Main game loop
running = True
clock = pygame.time.Clock()
last_spawn_time = 0

t = -300000


def spawn_bug():
    bugs_chances = {
        # chances of each bug spawning
        "devil-ant": 7,
        "red-ant": 25,
        "dragonfly": 30,
        "black": 40,
        "butterfly": 40,
        "green": 30,
        "jump": 40,
        "mosquito": 27,
        'bee': 30
    }
    bugs_keys = list(bugs_chances.keys())
    bugs_weights = list(bugs_chances.values())

    while True:
        d_t = pygame.time.get_ticks()-t

        if d_t < 90000:
            limit = 3
        elif d_t < 180000:
            limit = 7
        elif d_t < 240000:
            limit = 10
        elif d_t < 300000:
            limit = 15
        else:
            limit = 0

        if display_mode:
            limit = 5

        with game_data_lock:
            # Remove destroyed objects
            game_data["bugs"] = [b for b in game_data["bugs"] if not b.destroy]
            game_data["blood"] = [
                b for b in game_data["blood"] if not b.destroy]

            if len(game_data["bugs"]) < limit:
                chosen_bug = random.choices(bugs_keys, weights=bugs_weights)[0]
                game_data["bugs"].append(Bug(chosen_bug))

        time.sleep(1/5)


# Start the spawn_bug function in a separate thread
spawn_thread = threading.Thread(target=spawn_bug)
spawn_thread.daemon = True
spawn_thread.start()
last_fire_time = 0
bullet_count = 6
reloading = False
reload_time = 0

gun_stats = {
    "pistol": {
        "fire_rate": 1000/6,
        "reload_time": 2000,
        "max_ammo": 6,
        "hit_type": "single"
    },
    "shotgun": {
        "fire_rate": 1000/2,
        "reload_time": 1500,
        "max_ammo": 2,
        "hit_type": "wide"
    }

}
bullet_count = gun_stats["pistol"]["max_ammo"]
rate_of_fire = gun_stats["pistol"]["fire_rate"]
hit_type = gun_stats["pistol"]["hit_type"]
max_ammo = gun_stats["pistol"]["max_ammo"]
reload_duration = gun_stats["pistol"]["reload_time"]

# Pre-build flashbang surface (reused every frame)
_flash_surface_opaque = pygame.Surface((800, 600))
_flash_surface_opaque.fill((255, 255, 255))
_flash_surface_alpha = pygame.Surface((800, 600), pygame.SRCALPHA)


def check_collision(x, y, x_bug, y_bug, hit_type):
    if hit_type == "single":
        return x_bug < x < x_bug + 100 and y_bug + 25 < y < y_bug + 75
    elif hit_type == "wide":
        cursor_radius = 37
        closest_x = max(x_bug, min(x, x_bug + 100))
        closest_y = max(y_bug + 25, min(y, y_bug + 75))
        distance_x = x - closest_x
        distance_y = y - closest_y
        return distance_x**2 + distance_y**2 <= cursor_radius**2


def loading(x, y, angle):
    loading_surface = pygame.transform.rotate(assets["loading"], 360 - angle)
    length = loading_surface.get_width()
    height = loading_surface.get_height()
    loading_surface = loading_surface.subsurface(
        (length//2-10, height//2-10, 20, 20))
    screen.blit(loading_surface, (x, y))


def pie(radius, start_angle, end_angle, x, y, screen):
    pointlist = []
    for angle in range(start_angle, end_angle+1):
        x1 = x + radius * math.cos(math.radians(angle))
        y1 = y + radius * math.sin(math.radians(angle))
        pointlist.append((x1, y1))
    pygame.draw.polygon(screen, (0, 0, 0), pointlist)


def map_range(v, in_min, in_max, out_min, out_max):
    return (v - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


# Reusable surface for oi-oi-oi overlay
_oi_surface = pygame.Surface((800, 600))


def play_oi_oi_oi(frame_index, opacity=255):
    x, y = pygame.mouse.get_pos()
    l_x = map_range(x, 0, 800, 0, 128)
    l_y = map_range(y, 0, 600, -74, 74)
    g_x = map_range(x, 0, 800, -32, 32)
    g_y = map_range(y, 0, 600, -32, 32)
    _oi_surface.fill((255, 255, 255))
    _oi_surface.blit(assets["oi-oi-oi"][frame_index], (l_x, l_y))
    _oi_surface.blit(assets["minigun"], (g_x, g_y))
    _oi_surface.set_alpha(opacity)
    screen.blit(_oi_surface, (0, 0))


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # flash banged
            if event.key == pygame.K_f:
                flash_banged = pygame.time.get_ticks()
                # 2/3 chances of type 0 flash, 1/3 chances of type 1
                flashbang_type = random.choices([0, 1], weights=[2, 1])[0]
                if flashbang_type == 0:
                    pygame.mixer.Channel(2).play(assets["stun"])
                else:
                    pygame.mixer.Channel(2).play(assets["oi"])
            if event.key == pygame.K_p:
                flash_banged = pygame.time.get_ticks()
                flashbang_type = 0
            if event.key == pygame.K_g:
                t = pygame.time.get_ticks()
                game_data["score"] = 0
            if event.key == pygame.K_h:
                game_data["score"] = 0
            if event.key == pygame.K_m:
                display_mode = not display_mode
            if event.key == pygame.K_n:
                t = pygame.time.get_ticks()-300000

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not reloading and (pygame.time.get_ticks() - last_fire_time) >= rate_of_fire:
                if bullet_count > 0:
                    bullet_count -= 1
                    last_fire_time = pygame.time.get_ticks()
                    x, y = pygame.mouse.get_pos()
                    pygame.mixer.Channel(0).play(assets["fire"])
                    with game_data_lock:
                        bugs_snapshot = list(game_data["bugs"])
                    for bug in bugs_snapshot:
                        x_bug, y_bug = bug.get_position()
                        if check_collision(x, y, x_bug, y_bug, hit_type):
                            with game_data_lock:
                                if bug in game_data["bugs"]:
                                    game_data["bugs"].remove(bug)
                            pygame.mixer.Channel(1).play(assets["blood"])
                            game_data["blood"].append(Blood(x_bug, y_bug))
                            score_delta = {
                                "butterfly": -2,
                                "green": 3,
                                "dragonfly": -3,
                                "red-ant": 2,
                                "black": -3,
                                "jump": 3,
                                "mosquito": 2,
                                "bee": 2,
                            }.get(bug.name, 0)
                            if bug.name == "devil-ant":
                                flashbang_type = random.choices(
                                    [0, 1], weights=[2, 1])[0]
                                flash_banged = pygame.time.get_ticks()
                                if flashbang_type == 0:
                                    pygame.mixer.Channel(
                                        2).play(assets["stun"])
                                    score_delta = 10
                                else:
                                    pygame.mixer.Channel(2).play(assets["oi"])
                                    score_delta = 20
                            game_data["score"] += score_delta
                            if game_data["score"] < 0:
                                game_data["score"] = 0
                else:
                    pygame.mixer.Channel(0).play(assets["empty"])
            elif event.button == 3 and not reloading:
                pygame.mixer.Channel(0).play(assets["reload"])
                reloading = True
                reload_time = pygame.time.get_ticks()
                bullet_count = 0
            # only allow weapon switching if not reloading and after time limit
            if not reloading and (display_mode or pygame.time.get_ticks() - t > 30000):
                if event.button == 4:
                    # Scroll up to switch to pistol
                    bullet_count = gun_stats["pistol"]["max_ammo"]
                    rate_of_fire = gun_stats["pistol"]["fire_rate"]
                    hit_type = gun_stats["pistol"]["hit_type"]
                    max_ammo = gun_stats["pistol"]["max_ammo"]
                    reload_duration = gun_stats["pistol"]["reload_time"]
                    pygame.mixer.Channel(0).play(assets["gun-cock"])
                if event.button == 5:
                    # Scroll down to switch to shotgun
                    bullet_count = gun_stats["shotgun"]["max_ammo"]
                    rate_of_fire = gun_stats["shotgun"]["fire_rate"]
                    hit_type = gun_stats["shotgun"]["hit_type"]
                    max_ammo = gun_stats["shotgun"]["max_ammo"]
                    reload_duration = gun_stats["shotgun"]["reload_time"]
                    pygame.mixer.Channel(0).play(assets["gun-cock"])

    # Draw everything
    screen.blit(background, (0, 0))

    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, pygame.Color('white'))
    screen.blit(fps_text, (400, 10))

    with game_data_lock:
        bugs_snapshot = list(game_data["bugs"])
        blood_snapshot = list(game_data["blood"])

    for bug in bugs_snapshot:
        bug.draw(screen)

    for blood in blood_snapshot:
        blood.draw(screen)

    # Flashbang effect
    if flash_banged:
        elapsed_time = pygame.time.get_ticks() - flash_banged
        if flashbang_type == 0:
            if elapsed_time < 3000:
                screen.blit(_flash_surface_opaque, (0, 0))
            elif elapsed_time < 5000:
                alpha = int(255 * (1 - (elapsed_time - 3000) / 2000))
                _flash_surface_alpha.fill((255, 255, 255, alpha))
                screen.blit(_flash_surface_alpha, (0, 0))
            else:
                flash_banged = 0
        else:
            fps_oi = 30
            c = (pygame.time.get_ticks() - flash_banged) // (1000 // fps_oi) % 398
            if elapsed_time < 10000:
                play_oi_oi_oi(c)
            elif elapsed_time < 13266:
                alpha = int(255 * (1 - (elapsed_time - 10000) / 3266))
                play_oi_oi_oi(c, alpha)
            else:
                flash_banged = 0
    # Render the score
    score_text = font.render(
        f"{game_data['score']:08d}", True, (255, 255, 255))
    # Position the score at the upper left corner
    screen.blit(score_text, (10, 10))

    bullet_message = f"{bullet_count}/{max_ammo} "
    if reloading:
        # take 2 seconds to reload
        if pygame.time.get_ticks() - reload_time > reload_duration:
            reloading = False
            bullet_count = max_ammo
            pygame.mixer.Channel(0).play(assets["gun-cock"])
        angle = (pygame.time.get_ticks() - reload_time) / reload_duration * 720
        loading(45, 280, angle)
    colour = (255, 255, 255)
    if not reloading and bullet_count == 0:
        colour = (255, 0, 0)
    bullet_count_text = font.render(bullet_message, True, colour)
    screen.blit(bullet_count_text, (10, 280))

    d_t = pygame.time.get_ticks()-t
    # count down from 3 minutes
    time_left = 300000-d_t
    if time_left < 0:
        time_left = 0
    time_left = time_left//1000
    minutes = time_left//60
    seconds = time_left % 60
    time_text = font.render(
        f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
    if not display_mode:
        screen.blit(time_text, (700, 10))
    if hit_type == "single":
        pygame.draw.circle(screen, (0, 0, 0), pygame.mouse.get_pos(), 5)
    if hit_type == "wide":
        x, y = pygame.mouse.get_pos()
        pie(37, 30, 60, x, y, screen)
        pie(37, 120, 150, x, y, screen)
        pie(37, 210, 240, x, y, screen)
        pie(37, 300, 330, x, y, screen)

    screen.blit(assets[f"{hit_type}{bullet_count}"], (10, 305))

    pygame.display.flip()
    clock.tick(max_fps)

pygame.quit()
