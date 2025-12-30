import pygame
import math
import random

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()

# ЗАПУСК НА ВЕСЬ ЭКРАН
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Pink Magical Heart 💖")
clock = pygame.time.Clock()

# --- ЦВЕТА (РОЗОВАЯ ПАЛИТРА) ---
BG_COLOR = (20, 10, 35)
HEART_OUTLINE = (255, 20, 147)  # Hot Pink
HEART_MID = (255, 105, 180)     # Светлее
HEART_CENTER = (255, 192, 203)  # Нежно-розовый
HEART_DEEP = (180, 40, 120)     # Глубокий розово-фиолетовый
SPARKLE_COL = (255, 255, 240)   # Кремовый

# Звезды: Фиолетовые, Розовые, Голубые, Белые
STAR_COLORS = [(186, 85, 211), (255, 105, 180), (135, 206, 250), (255, 255, 255)]

# --- ФОРМУЛА ---
def get_heart_pos(t, scale):
    x = 16 * math.pow(math.sin(t), 3)
    y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
    return x * scale * 1.1, -y * scale

# --- ФОН ---
class BackgroundStar:
    def __init__(self):
        self.reset(random_y=True)
    def reset(self, random_y=False):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT) if random_y else HEIGHT + 10
        self.speed = random.uniform(0.4, 1.2)
        self.color = random.choice(STAR_COLORS)
        self.size = random.randint(1, 4) # Чуть крупнее для большого экрана
        self.alpha = random.randint(50, 180)
    def update(self):
        self.y -= self.speed
        if self.y < -10: self.reset()
    def draw(self, surface):
        col = [max(0, c - (255 - self.alpha)) for c in self.color]
        pygame.draw.rect(surface, col, (self.x, self.y, self.size, self.size))

# --- ПИКСЕЛЬ (СБАЛАНСИРОВАННАЯ СКОРОСТЬ) ---
class ChaoticPixel:
    def __init__(self):
        self.t = random.uniform(0, 2 * math.pi)
        self.r = math.pow(random.random(), 0.4)

        # СКОРОСТЬ (Золотая середина)
        self.vt = random.uniform(-0.025, 0.025)
        self.vr = random.uniform(-0.012, 0.012)

        self.size = random.choice([2, 3, 4])
        self.color = HEART_CENTER

    def update(self):
        # Импульсы
        self.vt += random.uniform(-0.001, 0.001)
        self.vr += random.uniform(-0.0005, 0.0005)

        # Инерция
        self.vt *= 0.985
        self.vr *= 0.985

        self.t += self.vt
        self.r += self.vr

        # Отскок
        if self.r > 1.0:
            self.r = 1.0
            self.vr *= -1
        if self.r < 0.05:
            self.r = 0.05
            self.vr *= -1

        # Цвет (Розовый градиент)
        if self.r > 0.9: self.color = HEART_OUTLINE
        elif self.r > 0.6: self.color = HEART_MID
        elif self.r > 0.3: self.color = HEART_CENTER
        else: self.color = HEART_DEEP

    def draw(self, surface, cx, cy, scale):
        hx, hy = get_heart_pos(self.t, scale)
        px = cx + hx * self.r
        py = cy + hy * self.r
        pygame.draw.rect(surface, self.color, (px, py, self.size, self.size))

# --- БЛЕСТКИ ---
class Sparkle:
    def __init__(self, cx, cy, scale):
        t = random.uniform(0, 2 * math.pi)
        hx, hy = get_heart_pos(t, scale)
        self.x = cx + hx
        self.y = cy + hy
        angle = math.atan2(hy, hx)
        speed = random.uniform(4, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.col = random.choice([HEART_OUTLINE, SPARKLE_COL, (255, 255, 255)])
        self.size = random.randint(3, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.life -= 6

    def draw(self, surface):
        if self.life > 0:
            fade = self.life / 255
            c = (int(self.col[0] * fade), int(self.col[1] * fade), int(self.col[2] * fade))
            pygame.draw.rect(surface, c, (self.x, self.y, self.size, self.size))

# --- SETUP ---
# 5000 частиц для плотности на большом экране
pixels = [ChaoticPixel() for _ in range(5000)]
bg_stars = [BackgroundStar() for _ in range(100)]
sparkles = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Кнопка ESC для выхода
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # --- ШЛЕЙФ ---
    fade_surf = pygame.Surface((WIDTH, HEIGHT))
    # Alpha 20 - красивый длинный след
    fade_surf.set_alpha(20)
    fade_surf.fill(BG_COLOR)
    screen.blit(fade_surf, (0, 0))

    # Фон
    for star in bg_stars:
        star.update()
        star.draw(screen)

    # --- РИТМ ---
    t_ms = pygame.time.get_ticks()
    phase = t_ms % 1300
    beat = 0
    if 0 <= phase < 150:
        beat = math.sin((phase / 150) * math.pi) * 1.0
    elif 250 <= phase < 400:
        beat = math.sin(((phase - 250) / 150) * math.pi) * 0.6

    # --- АВТОМАТИЧЕСКИЙ МАСШТАБ ---
    base_scale = min(WIDTH, HEIGHT) // 45
    scale = base_scale + (beat * (base_scale * 0.3))
    cx, cy = WIDTH // 2, HEIGHT // 2

    # --- ОТРИСОВКА ---
    for p in pixels:
        p.update()
        p.draw(screen, cx, cy, scale)

    if beat > 0.5:
        for _ in range(20):
            sparkles.append(Sparkle(cx, cy, scale))

    for s in sparkles[:]:
        s.update()
        s.draw(screen)
        if s.life <= 0:
            sparkles.remove(s)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()