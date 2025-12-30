import pygame
import math
import random
import os
import numpy as np

# --- НАСТРОЙКИ ---
FPS = 60
PARTICLE_COUNT = 3000
STAR_COUNT = 150

# ЦВЕТА
BG_COLOR = (10, 5, 20)
COLOR_IDLE = (255, 20, 100)
COLOR_MID = (200, 50, 255)
COLOR_PEAK = (0, 255, 255)
COLOR_FLASH = (255, 255, 255)

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
CX, CY = WIDTH // 2, HEIGHT // 2

pygame.display.set_caption("ULTIMATE BASS HEART 💖")
clock = pygame.time.Clock()


# --- МАТЕМАТИКА ---
def get_heart_pos(t):
    x = 16 * math.pow(math.sin(t), 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x, -y


MAX_FORMULA_RADIUS = 18.0
SAFE_MAX_SCALE = (min(WIDTH, HEIGHT) / 2) / MAX_FORMULA_RADIUS
BASE_SCALE = SAFE_MAX_SCALE * 0.35

# --- ПЛЕЕР ---
playlist = []
current_track_index = 0
sound_obj = None
sound_arr = None
start_ticks = 0
song_length_sec = 0


def get_music_files():
    folder = "Music"
    if not os.path.exists(folder): os.makedirs(folder); return []
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.mp3', '.wav'))]
    files.sort()
    return files


def play_track(index):
    global sound_obj, sound_arr, start_ticks, song_length_sec, current_track_index
    if not playlist: return

    # Останавливаем текущий
    if sound_obj: sound_obj.stop()

    # Python умеет работать с отрицательными индексами (-1 это последний элемент),
    # так что логика "назад" работает сама собой через %.
    current_track_index = index % len(playlist)
    path = playlist[current_track_index]

    print(f"PLAYING [{current_track_index + 1}/{len(playlist)}]: {path}")

    try:
        sound_obj = pygame.mixer.Sound(path)
        sound_arr = pygame.sndarray.array(sound_obj)
        song_length_sec = sound_obj.get_length()
        sound_obj.play(loops=0)
        start_ticks = pygame.time.get_ticks()
    except Exception as e:
        print(f"Error playing {path}: {e}")
        # Если ошибка, пробуем следующий, но с защитой от рекурсии (просто +1)
        # play_track(current_track_index + 1) - опасно если все файлы битые, лучше пропустить


playlist = get_music_files()
if playlist: play_track(0)


# --- ЭФФЕКТЫ ---

class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(-WIDTH, WIDTH)
        self.y = random.randint(-HEIGHT, HEIGHT)
        self.z = random.randint(WIDTH // 2, WIDTH)
        self.size = random.randint(1, 3)
        self.color = random.choice([(100, 100, 255), (255, 100, 255), (255, 255, 255)])

    def update(self, speed_boost):
        speed = 10 + (speed_boost * 100)
        self.z -= speed
        if self.z <= 1: self.reset()

    def draw(self, surface):
        factor = 400 / self.z
        sx = CX + self.x * factor
        sy = CY + self.y * factor
        if 0 < sx < WIDTH and 0 < sy < HEIGHT:
            size = self.size * (factor * 0.5)
            col = self.color
            if factor > 2:
                prev_factor = 400 / (self.z + 20)
                px = CX + self.x * prev_factor
                py = CY + self.y * prev_factor
                pygame.draw.line(surface, col, (px, py), (sx, sy), int(max(1, size)))
            else:
                pygame.draw.rect(surface, col, (sx, sy, max(1, size), max(1, size)))


class Shockwave:
    def __init__(self, radius, color, width, speed):
        self.radius = radius
        self.color = color
        self.width = width
        self.speed = speed
        self.active = True
        self.alpha = 255

    def update(self):
        self.radius += self.speed
        self.width -= 0.2
        self.alpha -= 6
        if self.alpha <= 0 or self.width < 1: self.active = False

    def draw(self, surface):
        if not self.active or self.radius > max(WIDTH, HEIGHT): return
        rect = pygame.Rect(CX - self.radius, CY - self.radius, self.radius * 2, self.radius * 2)
        if self.width > 1:
            pygame.draw.arc(surface, self.color, rect, 0, 6.28, int(self.width))


class HeartParticle:
    def __init__(self):
        self.t = random.uniform(0, 2 * math.pi)
        self.target_r = math.pow(random.random(), 0.3)
        self.current_r = self.target_r
        self.speed_t = random.uniform(0.002, 0.006) * random.choice([-1, 1])
        self.size = random.randint(2, 4)
        self.color = COLOR_IDLE

    def update(self, bass_power):
        self.t += self.speed_t
        expand = (bass_power ** 3) * 0.8
        self.current_r = self.target_r + expand
        if bass_power > 0.8:
            self.color = COLOR_PEAK if random.random() > 0.3 else COLOR_FLASH
            self.size = random.randint(3, 5)
        elif bass_power > 0.4:
            self.color = COLOR_MID
            self.size = random.randint(2, 4)
        else:
            self.color = COLOR_IDLE
            self.size = random.randint(1, 3)

    def draw(self, surface, scale, shake_x, shake_y, offset_rgb=(0, 0)):
        hx, hy = get_heart_pos(self.t)
        px = CX + (hx * scale * self.current_r) + shake_x + offset_rgb[0]
        py = CY + (hy * scale * self.current_r) + shake_y + offset_rgb[1]
        if 0 < px < WIDTH and 0 < py < HEIGHT:
            pygame.draw.rect(surface, self.color, (px, py, self.size, self.size))


# --- ГЛОБАЛЬНЫЕ ---
stars = [Star() for _ in range(STAR_COUNT)]
particles = [HeartParticle() for _ in range(PARTICLE_COUNT)]
shockwaves = []
smooth_bass = 0
max_bass_detected = 10000.0

running = True
while running:
    # --- ОБРАБОТКА СОБЫТИЙ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # --- ЛИСТАНИЕ ТРЕКОВ ---
            elif event.key == pygame.K_RIGHT:
                # Следующий трек
                play_track(current_track_index + 1)
                smooth_bass = 0  # Сброс визуализации, чтобы не дергалось

            elif event.key == pygame.K_LEFT:
                # Предыдущий трек
                play_track(current_track_index - 1)
                smooth_bass = 0

    # --- АВТОМАТИЧЕСКОЕ ПЕРЕКЛЮЧЕНИЕ ---
    if playlist and sound_obj:
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
        if elapsed >= song_length_sec - 0.1:
            play_track(current_track_index + 1)
            smooth_bass = 0
            elapsed = 0

    # --- АНАЛИЗ ---
    target_bass = 0
    if sound_arr is not None and playlist:
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0
        idx = int((elapsed * 44100) % sound_arr.shape[0])
        chunk = sound_arr[idx: idx + 2048]
        if len(chunk) > 100:
            if len(chunk.shape) > 1: chunk = chunk[:, 0]
            fft_val = np.abs(np.fft.rfft(chunk))
            raw_bass = np.sum(fft_val[1:7])

            if raw_bass > max_bass_detected:
                max_bass_detected = raw_bass
            else:
                max_bass_detected *= 0.992

            if max_bass_detected > 0: target_bass = raw_bass / max_bass_detected

    if target_bass < 0.1: target_bass = 0
    if target_bass > smooth_bass:
        smooth_bass = 0.5 * smooth_bass + 0.5 * target_bass
    else:
        smooth_bass = 0.9 * smooth_bass + 0.1 * target_bass

    # --- ЛОГИКА КАДРА ---
    bass_curve = smooth_bass ** 3
    scale = BASE_SCALE + (bass_curve * (SAFE_MAX_SCALE - BASE_SCALE) * 1.2)

    shake_x, shake_y = 0, 0
    if smooth_bass > 0.6:
        force = (smooth_bass - 0.6) * 35
        shake_x = random.randint(int(-force), int(force))
        shake_y = random.randint(int(-force), int(force))

    if smooth_bass > 0.75:
        if random.random() < (smooth_bass - 0.5):
            sw_color = COLOR_PEAK if smooth_bass < 0.9 else COLOR_FLASH
            sw_speed = 10 + (smooth_bass * 25)
            sw_width = 5 + (smooth_bass * 15)
            shockwaves.append(Shockwave(scale * 12, sw_color, sw_width, sw_speed))

    # --- ОТРИСОВКА ---
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BG_COLOR)
    fade.set_alpha(70 if smooth_bass > 0.6 else 40)
    screen.blit(fade, (0, 0))

    for s in stars:
        s.update(smooth_bass)
        s.draw(screen)

    for w in shockwaves[:]:
        w.update()
        w.draw(screen)
        if not w.active: shockwaves.remove(w)

    if smooth_bass > 0.85:
        for p in particles:
            p.update(smooth_bass)
            p.color = (255, 0, 0);
            p.draw(screen, scale, shake_x, shake_y, offset_rgb=(-15, 0))
            p.color = (0, 255, 255);
            p.draw(screen, scale, shake_x, shake_y, offset_rgb=(15, 0))
            p.color = (255, 255, 255);
            p.draw(screen, scale, shake_x, shake_y)
    else:
        for p in particles:
            p.update(smooth_bass)
            p.draw(screen, scale, shake_x, shake_y)

    if smooth_bass > 0.92:
        flash_surf = pygame.Surface((WIDTH, HEIGHT))
        flash_surf.fill(COLOR_FLASH)
        flash_surf.set_alpha(50)
        screen.blit(flash_surf, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()