import pygame
import random
import math

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Minecraft New Year: Final Edition")
clock = pygame.time.Clock()

# --- НАСТРОЙКИ ---
FPS = 60
GRAVITY = 0.2
PARTICLE_SIZE = 6
SNOW_SIZE = 4
SCALE_FACTOR = 7
SPAWN_RATE = 40

# --- ЦВЕТА ---
BACKGROUND_COLOR = (10, 15, 30)
WHITE = (255, 255, 255)
BROWN = (100, 60, 20)
ORANGE = (255, 140, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREY_SHADOW = (200, 200, 220)

GREEN_PALETTE = [(0, 255, 0), (50, 205, 50), (34, 139, 34), (0, 128, 0), (144, 238, 144)]
LIGHTS_PALETTE = [(255, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]
SCARF_COLORS = [(200, 0, 0), (0, 0, 200), (0, 150, 0), (200, 200, 0), (150, 0, 150)]

# Группы спрайтов
text_particles = pygame.sprite.Group()
snow_sprites = pygame.sprite.Group()
mouse_sparkles = pygame.sprite.Group()
fireworks = pygame.sprite.Group()
snowmen_list = []


# --- КЛАСС СНЕЖИНКИ ---
class Snowflake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(snow_sprites)
        self.image = pygame.Surface((SNOW_SIZE, SNOW_SIZE))
        self.image.fill((220, 230, 255))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(-50, -10)
        self.speed_y = random.uniform(1.5, 4)
        self.wobble = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.02, 0.08)

    def update(self):
        self.rect.y += self.speed_y
        self.wobble += self.wobble_speed
        self.rect.x += math.sin(self.wobble) * 2
        if self.rect.y > HEIGHT:
            self.kill()
            Snowflake()


# --- КЛАСС ЧАСТИЦЫ ФЕЙЕРВЕРКА ---
class FireworkParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__(fireworks)
        self.image = pygame.Surface((5, 5))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.timer = random.randint(30, 50)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 0.15
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
        elif self.timer < 15:
            if self.timer % 2 == 0:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)


# --- КЛАСС ПРОДВИНУТОГО СНЕГОВИКА ---
class AdvancedSnowman:
    def __init__(self):
        self.scale = random.uniform(0.7, 1.3)
        self.r_bot = 22 * self.scale
        self.r_mid = 16 * self.scale
        self.r_top = 11 * self.scale
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(HEIGHT - 60, HEIGHT - 10)
        self.speed = random.uniform(0.5, 1.5) * random.choice([-1, 1])
        self.scarf_color = random.choice(SCARF_COLORS)
        self.anim_timer = random.uniform(0, 100)

    def update(self):
        self.x += self.speed
        if self.x < 30:
            self.speed = abs(self.speed)
        elif self.x > WIDTH - 30:
            self.speed = -abs(self.speed)
        self.anim_timer += 0.15

    def draw(self, surface):
        bob_y = abs(math.sin(self.anim_timer)) * (4 * self.scale)
        tilt = math.sin(self.anim_timer) * 2

        center_bot = (self.x, self.y - self.r_bot)
        cy_mid = self.y - (self.r_bot * 1.8) - self.r_mid - bob_y
        center_mid = (self.x + tilt, cy_mid)
        cy_top = cy_mid - self.r_mid * 0.8 - self.r_top
        head_sway = math.sin(self.anim_timer) * (2 * self.scale)
        center_top = (self.x + tilt + head_sway, cy_top)

        shadow_rect = pygame.Rect(0, 0, self.r_bot * 2.5, self.r_bot * 0.8)
        shadow_rect.center = (self.x, self.y)
        shadow_surf = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect)

        pygame.draw.circle(surface, WHITE, center_bot, self.r_bot)
        pygame.draw.circle(surface, WHITE, center_mid, self.r_mid)
        pygame.draw.circle(surface, WHITE, center_top, self.r_top)

        dir_facing = 1 if self.speed > 0 else -1
        btn_offset_x = dir_facing * (2 * self.scale)
        pygame.draw.circle(surface, BLACK, (center_mid[0] + btn_offset_x, center_mid[1] - self.r_mid * 0.3),
                           2 * self.scale)
        pygame.draw.circle(surface, BLACK, (center_mid[0] + btn_offset_x, center_mid[1] + self.r_mid * 0.3),
                           2 * self.scale)

        eye_x_offset = dir_facing * (4 * self.scale)
        eye_y = center_top[1] - (2 * self.scale)
        pygame.draw.circle(surface, BLACK, (center_top[0] + eye_x_offset, eye_y), 1.5 * self.scale)
        pygame.draw.circle(surface, BLACK, (center_top[0] + eye_x_offset + (dir_facing * 3 * self.scale), eye_y),
                           1.5 * self.scale)

        nose_start = (center_top[0] + eye_x_offset + (dir_facing * 1.5 * self.scale), eye_y + (3 * self.scale))
        nose_end = (nose_start[0] + (dir_facing * 8 * self.scale), nose_start[1])
        nose_top = (nose_start[0], nose_start[1] - (2 * self.scale))
        pygame.draw.polygon(surface, ORANGE, [nose_start, nose_end, nose_top])

        arm_swing = math.cos(self.anim_timer) * (15 * self.scale)
        shoulder_left = (center_mid[0] - self.r_mid * 0.8, center_mid[1] - self.r_mid * 0.2)
        shoulder_right = (center_mid[0] + self.r_mid * 0.8, center_mid[1] - self.r_mid * 0.2)

        hand_l_end = (shoulder_left[0] - (10 * self.scale), shoulder_left[1] + (5 * self.scale) + arm_swing)
        hand_r_end = (shoulder_right[0] + (10 * self.scale), shoulder_right[1] + (5 * self.scale) - arm_swing)

        pygame.draw.line(surface, BROWN, shoulder_left, hand_l_end, max(1, int(2 * self.scale)))
        pygame.draw.line(surface, BROWN, shoulder_right, hand_r_end, max(1, int(2 * self.scale)))

        scarf_y = center_mid[1] - self.r_mid * 0.8
        pygame.draw.rect(surface, self.scarf_color,
                         (center_mid[0] - self.r_mid * 0.6, scarf_y, self.r_mid * 1.2, 4 * self.scale))
        tail_end_x = center_mid[0] - (dir_facing * 12 * self.scale)
        wind_scarf = math.sin(self.anim_timer * 2) * 2
        pygame.draw.line(surface, self.scarf_color, (center_mid[0], scarf_y),
                         (tail_end_x, scarf_y + 10 * self.scale + wind_scarf), int(4 * self.scale))

        hat_w = self.r_top * 1.6
        hat_h = self.r_top * 1.2
        hat_y = center_top[1] - self.r_top * 0.8 - hat_h
        hat_x = center_top[0] - hat_w / 2

        pygame.draw.rect(surface, (20, 20, 20),
                         (center_top[0] - self.r_top, center_top[1] - self.r_top * 0.9, self.r_top * 2, 3 * self.scale))
        pygame.draw.rect(surface, (40, 40, 40), (hat_x, hat_y, hat_w, hat_h))
        pygame.draw.rect(surface, RED, (hat_x, hat_y + hat_h - 4 * self.scale, hat_w, 4 * self.scale))


# --- КЛАСС ЕЛКИ ---
class ChristmasTree:
    def __init__(self, x_center, y_bottom, block_size=12):
        self.blocks = []
        self.block_size = block_size
        self.origin_x = x_center
        self.origin_y = y_bottom
        self.sway_offset = random.uniform(0, 100)

        trunk_w, trunk_h = 3, 4
        trunk_x = x_center - (trunk_w * block_size) // 2
        trunk_y = y_bottom - trunk_h * block_size
        for i in range(trunk_w):
            for j in range(trunk_h):
                rel_x = (trunk_x + i * block_size) - x_center
                rel_y = (trunk_y + j * block_size) - y_bottom
                self.blocks.append({'rel_x': rel_x, 'rel_y': rel_y, 'color': BROWN, 'is_light': False, 'h': abs(rel_y)})

        layers = [(13, 4), (11, 6), (9, 8), (7, 10), (5, 12), (3, 14), (1, 15)]
        for width_blocks, height_offset in layers:
            layer_y_pos = y_bottom - (height_offset * block_size)
            start_x = x_center - (width_blocks * block_size) // 2
            for i in range(width_blocks):
                rel_x = (start_x + i * block_size) - x_center
                rel_y = layer_y_pos - y_bottom
                is_light = random.random() < 0.2
                color = random.choice(LIGHTS_PALETTE) if is_light else random.choice(GREEN_PALETTE)
                self.blocks.append(
                    {'rel_x': rel_x, 'rel_y': rel_y, 'color': color, 'is_light': is_light, 'h': abs(rel_y)})

    def update(self):
        if random.random() < 0.1:
            for block in self.blocks:
                if block['is_light'] and random.random() < 0.1:
                    block['color'] = random.choice(LIGHTS_PALETTE)

    def draw(self, surface):
        t = pygame.time.get_ticks() * 0.002
        for block in self.blocks:
            wind = math.sin(t + self.sway_offset) * (block['h'] * 0.05)
            draw_x = self.origin_x + block['rel_x'] + wind
            draw_y = self.origin_y + block['rel_y']
            pygame.draw.rect(surface, block['color'], (draw_x, draw_y, self.block_size, self.block_size))


# --- ИСКРЫ И ЧАСТИЦЫ ---
class MouseSparkle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(mouse_sparkles)
        self.image = pygame.Surface((4, 4))
        self.image.fill(random.choice(LIGHTS_PALETTE))
        self.rect = self.image.get_rect(center=pos)
        self.vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.alpha = 255

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.alpha -= 10
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(text_particles)
        self.image = pygame.Surface((PARTICLE_SIZE, PARTICLE_SIZE))
        self.color = random.choice(GREEN_PALETTE)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = [random.uniform(-3, 3), random.uniform(-4, 0)]
        self.gravity = GRAVITY
        self.alpha = 255

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.alpha -= 4
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


# --- ГЕНЕРАЦИЯ ТЕКСТА ---
def create_colored_pixel_text(text):
    font = pygame.font.Font(None, 24)
    temp_surf = font.render(text, False, (255, 255, 255), (0, 0, 0))
    w, h = temp_surf.get_size()
    colored_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        for y in range(h):
            if temp_surf.get_at((x, y))[0] > 100:
                colored_surf.set_at((x, y), random.choice(GREEN_PALETTE))
    return pygame.transform.scale(colored_surf, (w * SCALE_FACTOR, h * SCALE_FACTOR))


pixel_text_image = create_colored_pixel_text("HAPPY NEW YEAR")

# --- СОЗДАНИЕ МИРА ---
left_tree = ChristmasTree(180, HEIGHT - 50, block_size=12)
right_tree = ChristmasTree(WIDTH - 180, HEIGHT - 50, block_size=12)

# Создаем 8 разных снеговиков
for i in range(8):
    snowmen_list.append(AdvancedSnowman())

for _ in range(150): Snowflake()

# --- ГЛАВНЫЙ ЦИКЛ ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    # 1. Фон (Снег)
    snow_sprites.update()
    snow_sprites.draw(screen)
    if len(snow_sprites) < 200: Snowflake()

    # 2. Фейерверки
    if random.random() < 0.04:
        fx, fy = random.randint(100, WIDTH - 100), random.randint(50, 400)
        c = random.choice(LIGHTS_PALETTE)
        for _ in range(35): FireworkParticle(fx, fy, c)
    fireworks.update()
    fireworks.draw(screen)

    # 3. Земля
    pygame.draw.rect(screen, (230, 230, 250), (0, HEIGHT - 55, WIDTH, 55))

    # 4. Елки
    left_tree.update()
    left_tree.draw(screen)
    right_tree.update()
    right_tree.draw(screen)

    # 5. Снеговики (Сортировка по Y для правильного перекрытия)
    snowmen_list.sort(key=lambda s: s.y)
    for snowman in snowmen_list:
        snowman.update()
        snowman.draw(screen)

    # 6. Текст (ИЗМЕНЕНИЯ ЗДЕСЬ)
    t = pygame.time.get_ticks()

    # Замедлили пульсацию (коэф. времени с 0.005 до 0.0015)
    pulse = 1.0 + 0.05 * math.sin(t * 0.003)

    # Замедлили парение вверх-вниз (коэф. времени с 0.003 до 0.001)
    hover = math.sin(t * 0.002) * 20

    cur_w, cur_h = int(pixel_text_image.get_width() * pulse), int(pixel_text_image.get_height() * pulse)
    text_scaled = pygame.transform.scale(pixel_text_image, (cur_w, cur_h))
    text_rect = text_scaled.get_rect(center=(WIDTH // 2, HEIGHT // 2 + hover))

    # Эмиттер частиц из текста
    for _ in range(SPAWN_RATE):
        rx, ry = random.randint(0, cur_w - 1), random.randint(0, cur_h - 1)
        try:
            if text_scaled.get_at((rx, ry))[3] > 0:
                Particle(text_rect.x + rx, text_rect.y + ry)
        except:
            pass

    text_particles.update()
    text_particles.draw(screen)
    screen.blit(text_scaled, text_rect)

    # 7. Мышка
    if random.random() < 0.9: MouseSparkle(pygame.mouse.get_pos())
    mouse_sparkles.update()
    mouse_sparkles.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()