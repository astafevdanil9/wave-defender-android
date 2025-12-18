 # -*- coding: utf-8 -*-
import pygame
import random
import sys
import os
import json
import math

pygame.init()
pygame.mixer.init()

# ---------------- ПЛАТФОРМА ----------------
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ

# ---------------- НАСТРОЙКИ ЭКРАНА ----------------
if IS_ANDROID:
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    SCALE_FACTOR = HEIGHT / 720
else:
    WIDTH, HEIGHT = 1000, 600  # Увеличил для лучшего обзора на ПК
    SCALE_FACTOR = 1

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Defender")
clock = pygame.time.Clock()
FPS = 60

# ---------------- СИСТЕМА УРОВНЕЙ ----------------
LEVELS = [
    {  # Уровень 1: Обучение
        "name": "TRAINING GROUNDS",
        "enemy_count": 12,
        "enemy_speed": 1.0,
        "spawn_rate": 1500,
        "bg_color": (30, 40, 60),
        "boss": False,
        "waves": 3
    },
    {  # Уровень 2: Усиление
        "name": "NIGHT ASSAULT",
        "enemy_count": 20,
        "enemy_speed": 1.3,
        "spawn_rate": 1200,
        "bg_color": (20, 25, 40),
        "boss": False,
        "waves": 4
    },
    {  # Уровень 3: Финальный
        "name": "FINAL STAND",
        "enemy_count": 30,
        "enemy_speed": 1.7,
        "spawn_rate": 900,
        "bg_color": (40, 20, 35),
        "boss": True,
        "waves": 5
    }
]

# ---------------- СОХРАНЕНИЯ ----------------
SAVE_FILE = "game_save.json"

def save_game():
    data = {
        "best_wave": best_wave,
        "coins": coins,
        "unlocked_levels": unlocked_levels,
        "upgrades": player_upgrades
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global best_wave, coins, unlocked_levels, player_upgrades
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            best_wave = data.get("best_wave", 0)
            coins = data.get("coins", 0)
            unlocked_levels = data.get("unlocked_levels", 1)
            player_upgrades = data.get("upgrades", {
                "health": 1, "speed": 1, "fire_rate": 1, "damage": 1,
                "jump": 1, "regen": 0
            })
            
            # Гарантируем наличие всех ключей
            default_upgrades = {
                "health": 1, "speed": 1, "fire_rate": 1, "damage": 1,
                "jump": 1, "regen": 0
            }
            
            for key in default_upgrades:
                if key not in player_upgrades:
                    player_upgrades[key] = default_upgrades[key]
    except:
        best_wave = 0
        coins = 0
        unlocked_levels = 1
        player_upgrades = {
            "health": 1, "speed": 1, "fire_rate": 1, "damage": 1,
            "jump": 1, "regen": 0
        }

# ---------------- ШРИФТЫ ----------------
def get_font(size):
    return pygame.font.Font(None, int(size * SCALE_FACTOR))

# Уменьшаем размеры шрифтов для лучшего размещения
font_tiny = get_font(14)  # Добавляем очень маленький шрифт
font_small = get_font(18)
font_medium = get_font(22)  # Уменьшен с 24
font_large = get_font(32)   # Уменьшен с 36
font_huge = get_font(42)    # Уменьшен с 48

# ---------------- ФУНКЦИИ ОТРИСОВКИ ----------------
def draw_main_menu():
    screen.fill(COLORS["bg"])
    
    # Заголовок с тенью
    title = font_huge.render("WAVE DEFENDER", True, COLORS["ui"])
    title_shadow = font_huge.render("WAVE DEFENDER", True, (0, 0, 0))
    title_x = WIDTH//2 - title.get_width()//2
    title_y = 40 if HEIGHT > 600 else 20
    screen.blit(title_shadow, (title_x + 3, title_y + 3))
    screen.blit(title, (title_x, title_y))
    
    # Подзаголовок
    subtitle = font_medium.render("Defend against endless waves", True, (200, 200, 220))
    subtitle_x = WIDTH//2 - subtitle.get_width()//2
    subtitle_y = title_y + title.get_height() + 10
    screen.blit(subtitle, (subtitle_x, subtitle_y))
    
    # Выбор уровня - динамическое расположение
    level_start_y = subtitle_y + subtitle.get_height() + 40
    level_spacing = 80 if HEIGHT > 600 else 70
    
    for i in range(len(LEVELS)):
        unlocked = i < unlocked_levels
        color = COLORS["button"] if unlocked else (80, 80, 80)
        hover_color = COLORS["button_hover"] if unlocked else (100, 100, 100)
        text_color = COLORS["text"] if unlocked else (120, 120, 120)
        
        rect_width = min(350, WIDTH - 100)
        rect = pygame.Rect(WIDTH//2 - rect_width//2, 
                          level_start_y + i * level_spacing, 
                          rect_width, 65)
        
        # Эффект при наведении (только для ПК)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos) and unlocked and not IS_ANDROID
        
        pygame.draw.rect(screen, hover_color if is_hover else color, rect, 0, 12)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, 12)
        
        # Сокращаем название уровня если слишком длинное
        level_name = LEVELS[i]['name']
        if len(level_name) > 15:
            level_name = level_name[:12] + "..."
        
        level_text = font_large.render(f"LEVEL {i+1}: {level_name}", True, text_color)
        text_rect = level_text.get_rect(center=rect.center)
        screen.blit(level_text, text_rect)
        
        # Информация об уровне (только если есть место)
        if rect.bottom + 20 < HEIGHT - 150:
            info_text = font_tiny.render(f"Enemies: {LEVELS[i]['enemy_count']} | Waves: {LEVELS[i].get('waves', 3)}", 
                                       True, (180, 180, 200))
            screen.blit(info_text, (rect.centerx - info_text.get_width()//2, rect.bottom - 15))
        
        if not unlocked:
            lock_text = font_tiny.render("LOCKED", True, (200, 200, 200))
            screen.blit(lock_text, (rect.right - 50, rect.centery - 8))
    
    # Монеты и рекорд (в углах)
    coin_text = font_medium.render(f"Coins: {coins}", True, COLORS["coin"])
    coin_x = 20
    coin_y = 20
    screen.blit(coin_text, (coin_x, coin_y))
    
    record_text = font_medium.render(f"Best: {best_wave}", True, COLORS["text"])
    record_x = WIDTH - record_text.get_width() - 20
    record_y = 20
    screen.blit(record_text, (record_x, record_y))
    
    # Управление (только для ПК) - проверяем есть ли место
    if not IS_ANDROID and HEIGHT > 500:
        controls_y = HEIGHT - 100
        controls = [
            "A/D or ←/→ - Move | W/SPACE - Jump",
            "B/Mouse Left - Shoot | ESC - Menu",
            "R - Restart | F - Auto-fire"
        ]
        
        # Проверяем, не накладываются ли контролы на кнопки
        if controls_y > level_start_y + len(LEVELS) * level_spacing + 50:
            for i, text in enumerate(controls):
                control_text = font_tiny.render(text, True, (180, 180, 200))
                control_x = WIDTH//2 - control_text.get_width()//2
                control_y = controls_y + i * 18
                screen.blit(control_text, (control_x, control_y))
    
    # Кнопки внизу
    button_width = min(180, WIDTH//2 - 40)
    button_margin = 20
    button_y = HEIGHT - 70
    
    # Проверяем, не накладываются ли кнопки на уровни
    if button_y > level_start_y + len(LEVELS) * level_spacing + 30:
        # Кнопка магазина
        shop_rect = pygame.Rect(WIDTH//2 - button_width - button_margin//2, button_y, button_width, 45)
        shop_hover = shop_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
        pygame.draw.rect(screen, COLORS["button_hover"] if shop_hover else COLORS["button"], shop_rect, 0, 8)
        pygame.draw.rect(screen, (255, 255, 255), shop_rect, 2, 8)
        shop_text = font_medium.render("UPGRADES", True, (255, 255, 255))
        screen.blit(shop_text, shop_text.get_rect(center=shop_rect.center))
        
        # Кнопка выхода
        quit_rect = pygame.Rect(WIDTH//2 + button_margin//2, button_y, button_width, 45)
        quit_hover = quit_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
        pygame.draw.rect(screen, (200, 80, 80) if quit_hover else (180, 60, 60), quit_rect, 0, 8)
        pygame.draw.rect(screen, (255, 255, 255), quit_rect, 2, 8)
        quit_text = font_medium.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_text, quit_text.get_rect(center=quit_rect.center))
    else:
        # Если места мало, делаем одну кнопку "UPGRADES" по центру
        shop_rect = pygame.Rect(WIDTH//2 - button_width, button_y, button_width * 2, 45)
        shop_hover = shop_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
        pygame.draw.rect(screen, COLORS["button_hover"] if shop_hover else COLORS["button"], shop_rect, 0, 8)
        pygame.draw.rect(screen, (255, 255, 255), shop_rect, 2, 8)
        shop_text = font_medium.render("UPGRADES", True, (255, 255, 255))
        screen.blit(shop_text, shop_text.get_rect(center=shop_rect.center))

def draw_upgrades_menu():
    screen.fill((30, 35, 60))
    
    title = font_huge.render("UPGRADES", True, COLORS["ui"])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    coin_text = font_large.render(f"Coins: {coins}", True, COLORS["coin"])
    screen.blit(coin_text, (WIDTH//2 - coin_text.get_width()//2, 90))
    
    upgrades = [
        ("HEALTH", "Max HP +1", 100 + player_upgrades["health"] * 50, "health", 10),
        ("SPEED", "Speed +25%", 120 + player_upgrades["speed"] * 60, "speed", 5),
        ("FIRE RATE", "Shoot faster", 150 + player_upgrades["fire_rate"] * 70, "fire_rate", 5),
        ("DAMAGE", "Damage +75%", 200 + player_upgrades["damage"] * 80, "damage", 5),
        ("JUMP", "Jump +20%", 80 + player_upgrades["jump"] * 40, "jump", 5),
        ("REGEN", "Health regen", 300 + player_upgrades["regen"] * 150, "regen", 3)
    ]
    
    # Рассчитываем доступную высоту для списка улучшений
    available_height = HEIGHT - 200  # Минус заголовок и кнопка назад
    item_height = min(75, available_height // len(upgrades))
    
    for i, (name, desc, price, key, max_level) in enumerate(upgrades):
        y = 140 + i * item_height
        level = player_upgrades[key]
        maxed = level >= max_level
        
        # Фон улучшения
        rect_width = WIDTH - 60
        rect = pygame.Rect(30, y, rect_width, item_height - 5)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos) and not maxed and not IS_ANDROID
        
        color = COLORS["button_hover"] if is_hover else COLORS["button"]
        if maxed:
            color = (80, 80, 80)
        elif coins < price:
            color = (100, 60, 60)
            
        pygame.draw.rect(screen, color, rect, 0, 8)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, 8)
        
        # Сокращаем название если слишком длинное
        display_name = name
        if len(name) > 10:
            display_name = name[:8] + ".."
        
        # Текст улучшения
        name_text = font_medium.render(f"{display_name} Lvl {level}/{max_level}", True, COLORS["text"])
        screen.blit(name_text, (40, y + 10))
        
        # Описание (сокращаем если нужно)
        display_desc = desc
        if len(desc) > 20:
            display_desc = desc[:18] + ".."
        desc_text = font_tiny.render(display_desc, True, (200, 200, 200))
        screen.blit(desc_text, (40, y + 35))
        
        # Цена
        if not maxed:
            price_text = font_medium.render(f"{price}", True, COLORS["coin"])
            price_x = rect.right - 100
            screen.blit(price_text, (price_x, y + 15))
            
            # Кнопка покупки
            buy_rect = pygame.Rect(rect.right - 70, y + 15, 55, 25)
            can_afford = coins >= price
            btn_color = COLORS["button"] if can_afford else (120, 60, 60)
            btn_hover = buy_rect.collidepoint(mouse_pos) and can_afford and not IS_ANDROID
            
            pygame.draw.rect(screen, COLORS["button_hover"] if btn_hover else btn_color, buy_rect, 0, 4)
            buy_text = font_tiny.render("BUY" if can_afford else "NO$", True, (255, 255, 255))
            screen.blit(buy_text, buy_text.get_rect(center=buy_rect.center))
        else:
            max_text = font_medium.render("MAX", True, (180, 180, 180))
            screen.blit(max_text, (rect.right - 80, y + 15))
    
    # Кнопка назад
    back_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT - 70, 180, 45)
    back_hover = back_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
    pygame.draw.rect(screen, COLORS["button_hover"] if back_hover else COLORS["button"], back_rect, 0, 8)
    back_text = font_medium.render("BACK", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

def draw_game_ui():
    # Полоска здоровья
    health_width = min(250, WIDTH * 0.3)
    health_percent = player.health / player.max_health
    health_color = COLORS["health"] if health_percent > 0.3 else (255, 50, 50)
    
    # Фон
    pygame.draw.rect(screen, (40, 40, 60), 
                    (20, 15, health_width, 20), 0, 4)
    # Полоска здоровья
    pygame.draw.rect(screen, health_color, 
                    (22, 17, (health_width - 4) * health_percent, 16), 0, 3)
    # Рамка
    pygame.draw.rect(screen, (255, 255, 255), 
                    (20, 15, health_width, 20), 1, 4)
    
    health_text = font_tiny.render(f"HP: {player.health:.0f}/{player.max_health}", True, COLORS["text"])
    screen.blit(health_text, (25, 38))
    
    # Прогресс волны
    wave_width = min(300, WIDTH * 0.4)
    
    if wave_system.current_wave < wave_system.waves:
        # Фон прогресса
        pygame.draw.rect(screen, (40, 40, 60), 
                        (WIDTH//2 - wave_width//2, 15, wave_width, 15), 0, 7)
        
        # Прогресс волны
        enemies_left = max(0, wave_system.enemies_per_wave - len(enemies) - 
                          (wave_system.enemies_spawned_this_wave - len([e for e in enemies])))
        wave_fill = 1 - (enemies_left / wave_system.enemies_per_wave)
        pygame.draw.rect(screen, COLORS["wave_indicator"], 
                        (WIDTH//2 - wave_width//2 + 2, 17, 
                         (wave_width - 4) * wave_fill, 11), 0, 5)
    
    # Текст волны
    if wave_system.current_wave < wave_system.waves:
        wave_text = font_tiny.render(f"Wave {wave_system.current_wave + 1}/{wave_system.waves}", 
                                   True, COLORS["text"])
    else:
        wave_text = font_tiny.render("BOSS WAVE", True, COLORS["boss"])
    
    screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, 35))
    
    # Монеты (правая сторона)
    coin_text = font_medium.render(f"${coins + coins_gained}", True, COLORS["coin"])
    coin_x = WIDTH - coin_text.get_width() - 20
    coin_y = 20
    screen.blit(coin_text, (coin_x, coin_y))
    
    # Автострельба индикатор (под монетами если есть место)
    if auto_shoot and coin_y + coin_text.get_height() + 20 < HEIGHT:
        auto_text = font_tiny.render("AUTO: ON", True, (100, 255, 100))
        screen.blit(auto_text, (coin_x, coin_y + coin_text.get_height() + 5))
    
    # Индикатор перезарядки (только если есть место внизу)
    if player.cooldown > 0 and HEIGHT > 400:
        reload_y = HEIGHT - 35
        reload_width = 80 * (1 - player.cooldown / player.fire_rate)
        pygame.draw.rect(screen, (60, 60, 80), 
                        (WIDTH//2 - 40, reload_y, 80, 8), 0, 4)
        pygame.draw.rect(screen, COLORS["bullet"], 
                        (WIDTH//2 - 38, reload_y + 2, reload_width * 0.96, 4), 0, 2)

# В функции draw_upgrades_menu также нужно обновить обработку кликов:
# В цикле обработки событий для UPGRADES заменяем:
    elif current_state == "UPGRADES":
        # Покупка улучшений
        upgrades = [
            ("health", 100 + player_upgrades["health"] * 50, 10),
            ("speed", 120 + player_upgrades["speed"] * 60, 5),
            ("fire_rate", 150 + player_upgrades["fire_rate"] * 70, 5),
            ("damage", 200 + player_upgrades["damage"] * 80, 5),
            ("jump", 80 + player_upgrades["jump"] * 40, 5),
            ("regen", 300 + player_upgrades["regen"] * 150, 3)
        ]
        
        for i, (key, price, max_level) in enumerate(upgrades):
            y = 140 + i * 70  # Изменяем в соответствии с новой высотой
            rect = pygame.Rect(30, y, WIDTH - 60, 70)
            buy_rect = pygame.Rect(rect.right - 70, y + 15, 55, 25)  # Обновляем координаты
            
            if buy_rect.collidepoint(mouse_pos) and player_upgrades[key] < max_level and coins >= price:
                coins -= price
                player_upgrades[key] += 1
                if coin_sound:
                    coin_sound.play()
                save_game()
                # Обновляем игрока если он существует
                if player:
                    player = Player(player_upgrades)
        
        # Кнопка назад
        back_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT - 70, 180, 45)  # Обновляем координаты
        if back_rect.collidepoint(mouse_pos):
            current_state = "MAIN_MENU"
# ---------------- ЗВУК ----------------
def load_sound(path, volume=0.5):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except:
        return None

# Заглушки звуков (создадим базовые если файлов нет)
try:
    shoot_sound = load_sound("sounds/shoot.wav", 0.4)
except:
    shoot_sound = None

try:
    hit_sound = load_sound("sounds/hit.wav", 0.6)
except:
    hit_sound = None

try:
    coin_sound = load_sound("sounds/coin.wav", 0.7)
except:
    coin_sound = None

try:
    level_up_sound = load_sound("sounds/level_up.wav", 0.8)
except:
    level_up_sound = None

# Фоновая музыка
try:
    pygame.mixer.music.load("sounds/bg_music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except:
    pass

# ---------------- ЦВЕТА ----------------
COLORS = {
    "bg": (20, 25, 40),
    "ui": (50, 150, 220),
    "health": (220, 80, 80),
    "coin": (255, 215, 0),
    "enemy": (180, 70, 180),
    "bullet": (100, 200, 255),
    "boss": (220, 50, 50),
    "text": (240, 240, 240),
    "button": (70, 130, 200),
    "button_hover": (90, 170, 250),
    "platform": (60, 50, 40),
    "wave_indicator": (100, 200, 100)
}

# ---------------- ВИРТУАЛЬНЫЕ КНОПКИ (Android) ----------------
if IS_ANDROID:
    class VirtualButton:
        def __init__(self, x, y, width, height, key, label=""):
            self.rect = pygame.Rect(x, y, width, height)
            self.key = key
            self.label = label
            self.pressed = False
            self.alpha = 150
            
        def draw(self, screen):
            color = COLORS["button"] if not self.pressed else COLORS["button_hover"]
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, self.alpha), s.get_rect(), 0, 15)
            pygame.draw.rect(s, (255, 255, 255, 200), s.get_rect(), 2, 15)
            screen.blit(s, self.rect)
            
            if self.label:
                text = font_small.render(self.label, True, (255, 255, 255))
                screen.blit(text, text.get_rect(center=self.rect.center))
                
        def check_touch(self, pos):
            was_pressed = self.pressed
            self.pressed = self.rect.collidepoint(pos)
            return self.pressed and not was_pressed
    
    buttons = {
        'left': VirtualButton(20, HEIGHT - 100, 80, 80, pygame.K_a, "←"),
        'right': VirtualButton(110, HEIGHT - 100, 80, 80, pygame.K_d, "→"),
        'jump': VirtualButton(WIDTH - 200, HEIGHT - 100, 80, 80, pygame.K_SPACE, "↑"),
        'shoot': VirtualButton(WIDTH - 100, HEIGHT - 100, 80, 80, pygame.K_b, "⚡")
    }

# ---------------- КЛАСС ИГРОКА ----------------
class Player:
    def __init__(self, upgrades):
        self.width = 40 * SCALE_FACTOR
        self.height = 60 * SCALE_FACTOR
        self.rect = pygame.Rect(WIDTH//4, HEIGHT - self.height - 30, self.width, self.height)
        # Гарантируем наличие всех ключей
        default_upgrades = {
            "health": 1, "speed": 1, "fire_rate": 1, "damage": 1,
            "jump": 1, "regen": 0
        }
        
        for key in default_upgrades:
            if key not in upgrades:
                upgrades[key] = default_upgrades[key]        
        # Характеристики с улучшениями
        self.max_health = 3 + upgrades["health"]
        self.health = self.max_health
        self.speed = 5 * SCALE_FACTOR * (1 + upgrades["speed"] * 0.25)  # Увеличена база
        self.fire_rate = max(5, 20 - upgrades["fire_rate"] * 3)  # Минимальный кулдаун
        self.damage = 1 + upgrades["damage"] * 0.75
        self.jump_force = 16 * SCALE_FACTOR * (1 + upgrades["jump"] * 0.2)
        self.regen_rate = upgrades["regen"] * 0.5  # Реген здоровья в секунду
        
        self.vel_y = 0
        self.gravity = 0.8 * SCALE_FACTOR
        self.on_ground = False
        self.cooldown = 0
        self.invincible = 0
        self.direction = 1
        
        # Анимация
        self.anim_frame = 0
        self.anim_timer = 0
        self.regen_timer = 0
        
        # Двойной прыжок
        self.jumps_left = 2
        self.last_jump_time = 0
        
    def move(self, keys, touch_input=None):
        dx = 0
        
        # Управление с клавиатуры
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.direction = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.direction = 1
            
        # Прыжок с клавиатуры
        current_time = pygame.time.get_ticks()
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.jumps_left > 0:
            if current_time - self.last_jump_time > 200:  # Защита от спама
                self.vel_y = -self.jump_force
                self.jumps_left -= 1
                self.on_ground = False
                self.last_jump_time = current_time
        
        # Android управление
        if IS_ANDROID and touch_input:
            if touch_input.get('left'):
                dx -= self.speed
                self.direction = -1
            if touch_input.get('right'):
                dx += self.speed
                self.direction = 1
            if touch_input.get('jump') and self.jumps_left > 0:
                if current_time - self.last_jump_time > 200:
                    self.vel_y = -self.jump_force
                    self.jumps_left -= 1
                    self.on_ground = False
                    self.last_jump_time = current_time
        
        # Обновление позиции
        self.rect.x += dx
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.width))
        
        # Гравитация
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 20)  # Ограничение максимальной скорости падения
        self.rect.y += self.vel_y
        
        # Проверка земли
        if self.rect.bottom >= HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30
            self.vel_y = 0
            self.on_ground = True
            self.jumps_left = 2  # Восстановление прыжков на земле
            
        # Кулдаун стрельбы
        if self.cooldown > 0:
            self.cooldown -= 1
            
        # Неуязвимость после удара
        if self.invincible > 0:
            self.invincible -= 1
            
        # Регенерация здоровья
        self.regen_timer += 1
        if self.regen_rate > 0 and self.regen_timer >= 60:  # Раз в секунду
            if self.health < self.max_health:
                self.health = min(self.max_health, self.health + self.regen_rate)
                effects.append(Effect(self.rect.centerx, self.rect.top - 20,
                                    "+", (100, 255, 100), 30))
            self.regen_timer = 0
            
        # Анимация
        self.anim_timer += 1
        if dx != 0 and self.on_ground:
            if self.anim_timer > 5:
                self.anim_frame = (self.anim_frame + 1) % 4
                self.anim_timer = 0
                
    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = self.fire_rate
            if shoot_sound:
                shoot_sound.play()
            # Создаем пучок пуль при высоком уровне урона
            bullets = []
            bullets.append(Bullet(self.rect.centerx + 20 * self.direction, 
                                self.rect.centery, 
                                self.direction, 
                                self.damage))
            
            # Дополнительные пули при высоком уровне улучшений
            if player_upgrades["damage"] >= 3:
                bullets.append(Bullet(self.rect.centerx + 20 * self.direction, 
                                    self.rect.centery - 15, 
                                    self.direction, 
                                    self.damage * 0.7))
                bullets.append(Bullet(self.rect.centerx + 20 * self.direction, 
                                    self.rect.centery + 15, 
                                    self.direction, 
                                    self.damage * 0.7))
            return bullets
        return []
        
    def take_damage(self, damage=1):
        if self.invincible <= 0:
            self.health -= damage
            self.invincible = 30
            if hit_sound:
                hit_sound.play()
            return True
        return False
        
    def draw(self):
        # Мигание при неуязвимости
        if self.invincible > 0 and self.invincible % 6 < 3:
            alpha = 128
        else:
            alpha = 255
            
        # Тело игрока
        color = list(COLORS["ui"])
        color.append(alpha)
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, s.get_rect(), 0, 10)
        screen.blit(s, self.rect)
        
        # Голова
        head_rect = pygame.Rect(self.rect.centerx - 10, self.rect.top - 5, 20, 20)
        pygame.draw.rect(screen, COLORS["ui"], head_rect, 0, 10)
        
        # Оружие
        gun_length = 20 + player_upgrades["fire_rate"] * 5
        gun_pos = (self.rect.right if self.direction == 1 else self.rect.left,
                  self.rect.centery)
        pygame.draw.rect(screen, (100, 100, 120), 
                        (gun_pos[0] - 5 if self.direction == 1 else gun_pos[0] - 15,
                         gun_pos[1] - 3, 
                         gun_length * self.direction, 6), 0, 3)
        
        # Индикатор прыжков
        if self.jumps_left < 2:
            jump_color = (255, 100, 100) if self.jumps_left == 0 else (255, 200, 100)
            pygame.draw.circle(screen, jump_color, 
                             (self.rect.centerx, self.rect.bottom + 10), 
                             5 if self.jumps_left == 1 else 3)

# ---------------- КЛАСС ПУЛИ ----------------
class Bullet:
    def __init__(self, x, y, direction, damage):
        self.rect = pygame.Rect(x - 5, y - 3, 15, 6)
        self.speed = 15 * SCALE_FACTOR * direction  # Увеличена скорость
        self.damage = damage
        self.color = COLORS["bullet"]
        self.trail = []
        
    def update(self):
        # Добавляем след
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        self.rect.x += self.speed
        return self.rect.right < 0 or self.rect.left > WIDTH
        
    def draw(self):
        # Отрисовка следа
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            radius = max(1, 3 * (i / len(self.trail)))
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(pos[0]), int(pos[1])), int(radius))
            
        # Сама пуля
        pygame.draw.rect(screen, self.color, self.rect, 0, 3)

# ---------------- КЛАСС ВРАГА ----------------
class Enemy:
    def __init__(self, level, speed_mult, is_boss=False, wave_num=1):
        size = random.randint(30, 50) * SCALE_FACTOR
        if is_boss:
            size *= 2.5
            
        self.rect = pygame.Rect(
            WIDTH + random.randint(50, 200),
            HEIGHT - size - 30,
            size, size
        )
        
        self.is_boss = is_boss
        self.speed = random.uniform(1.5, 3.0) * SCALE_FACTOR * speed_mult * (1 + (wave_num-1)*0.1)
        self.health = (3 if is_boss else 1) * level * (1 + (wave_num-1)*0.2)
        self.max_health = self.health
        self.value = 15 * (3 if is_boss else 1) * level * wave_num
        self.color = COLORS["boss"] if is_boss else COLORS["enemy"]
        self.flash_timer = 0
        self.wave_num = wave_num
        
        # Атака босса
        self.attack_cooldown = 0
        self.projectiles = []
        
    def update(self):
        self.rect.x -= self.speed
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        # Атака босса
        if self.is_boss and self.attack_cooldown <= 0:
            if random.random() < 0.01:  # 1% шанс атаковать каждый кадр
                self.attack_cooldown = 60
                self.projectiles.append(BossProjectile(self.rect.left, self.rect.centery))
        else:
            self.attack_cooldown -= 1
            
        # Обновление снарядов босса
        for proj in self.projectiles[:]:
            if proj.update():
                self.projectiles.remove(proj)
                
        return self.rect.right < 0
        
    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 5
        return self.health <= 0
        
    def draw(self):
        color = (255, 255, 255) if self.flash_timer > 0 else self.color
        
        # Тело врага
        pygame.draw.rect(screen, color, self.rect, 0, 8 if self.is_boss else 5)
        
        # Глаза для босса
        if self.is_boss:
            eye_size = self.rect.height // 6
            pygame.draw.circle(screen, (255, 255, 255), 
                             (self.rect.right - eye_size*2, self.rect.top + eye_size*2), 
                             eye_size)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (self.rect.right - eye_size*2, self.rect.top + eye_size*2), 
                             eye_size//2)
        
        # Полоска здоровья
        health_width = (self.rect.width - 10) * (self.health / self.max_health)
        health_y = self.rect.top - 15 if self.is_boss else self.rect.top - 8
        health_height = 8 if self.is_boss else 4
        pygame.draw.rect(screen, (60, 60, 80),
                        (self.rect.x + 5, health_y, self.rect.width - 10, health_height), 0, 2)
        pygame.draw.rect(screen, COLORS["health"],
                        (self.rect.x + 5, health_y, health_width, health_height), 0, 2)
        
        # Отрисовка снарядов босса
        for proj in self.projectiles:
            proj.draw()

# ---------------- КЛАСС СНАРЯДА БОССА ----------------
class BossProjectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.speed = -8 * SCALE_FACTOR
        self.color = (255, 100, 100)
        self.trail = []
        
    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 8:
            self.trail.pop(0)
            
        self.rect.x += self.speed
        
        # Проверка столкновения с игроком
        if player and self.rect.colliderect(player.rect):
            player.take_damage(2)  # Двойной урон от босса
            effects.append(Effect(self.rect.centerx, self.rect.centery,
                                "BOSS HIT!", COLORS["boss"], 30))
            return True
            
        return self.rect.right < 0
        
    def draw(self):
        # След
        for i, pos in enumerate(self.trail):
            alpha = int(200 * (i / len(self.trail)))
            radius = max(2, 6 * (i / len(self.trail)))
            pygame.draw.circle(screen, (*self.color, alpha), 
                             (int(pos[0]), int(pos[1])), int(radius))
        
        # Снаряд
        pygame.draw.circle(screen, self.color, self.rect.center, 10)
        pygame.draw.circle(screen, (255, 200, 200), self.rect.center, 6)

# ---------------- КЛАСС ЭФФЕКТОВ ----------------
class Effect:
    def __init__(self, x, y, text="", color=None, duration=30):
        self.x = x
        self.y = y
        self.text = text
        self.color = color or COLORS["text"]
        self.duration = duration
        self.life = duration
        
    def update(self):
        self.life -= 1
        self.y -= 0.5
        return self.life <= 0
        
    def draw(self):
        alpha = int(255 * (self.life / self.duration))
        text = font_small.render(self.text, True, self.color)
        text.set_alpha(alpha)
        screen.blit(text, (self.x - text.get_width()//2, self.y))

# ---------------- СИСТЕМА ВОЛН ----------------
class WaveSystem:
    def __init__(self, level_data):
        self.total_enemies = level_data["enemy_count"]
        self.waves = level_data.get("waves", 3)
        self.enemies_per_wave = self.total_enemies // self.waves
        self.current_wave = 0
        self.enemies_spawned_this_wave = 0
        self.wave_complete = False
        self.wave_cooldown = 0
        
    def should_spawn(self):
        if self.current_wave >= self.waves:
            return False
            
        if self.enemies_spawned_this_wave < self.enemies_per_wave:
            return True
            
        # Проверяем, закончена ли волна
        if not self.wave_complete and len(enemies) == 0:
            self.wave_complete = True
            self.wave_cooldown = 180  # 3 секунды перерыв между волнами
            return False
            
        return False
        
    def spawn_enemy(self, level_data, level_idx, is_boss=False):
        self.enemies_spawned_this_wave += 1
        return Enemy(level_idx + 1, level_data["enemy_speed"], is_boss, self.current_wave + 1)
        
    def update(self):
        if self.wave_complete and self.wave_cooldown > 0:
            self.wave_cooldown -= 1
            if self.wave_cooldown <= 0:
                self.current_wave += 1
                self.enemies_spawned_this_wave = 0
                self.wave_complete = False
                
                if self.current_wave < self.waves:
                    effects.append(Effect(WIDTH//2, 100, 
                                        f"WAVE {self.current_wave + 1}", 
                                        COLORS["wave_indicator"], 90))
                return True
        return False

# ---------------- ИНИЦИАЛИЗАЦИЯ ИГРЫ ----------------
def init_game(level_index):
    global player, bullets, enemies, effects, coins_gained
    global enemy_count, spawned_count, spawn_timer, level_complete
    global boss_spawned, current_level, wave_system, wave_spawn_timer
    
    current_level = level_index
    level_data = LEVELS[level_index]
    
    player = Player(player_upgrades)
    bullets = []
    enemies = []
    effects = []
    coins_gained = 0
    
    enemy_count = level_data["enemy_count"]
    spawned_count = 0
    spawn_timer = 0
    wave_spawn_timer = 0
    level_complete = False
    boss_spawned = False if level_data["boss"] else True
    
    # Инициализация системы волн
    wave_system = WaveSystem(level_data)
    
    # Сообщение о начале волны
    effects.append(Effect(WIDTH//2, HEIGHT//2, 
                         f"WAVE 1", 
                         COLORS["wave_indicator"], 90))
    
    return level_data

# ---------------- ИГРОВЫЕ ПЕРЕМЕННЫЕ ----------------
load_game()
current_state = "MAIN_MENU"
current_level = 0
player = None
bullets = []
enemies = []
effects = []
coins_gained = 0
enemy_count = 0
spawned_count = 0
spawn_timer = 0
wave_spawn_timer = 0
level_complete = False
boss_spawned = True
shake_timer = 0
wave_system = None
auto_shoot = False
auto_shoot_timer = 0

# ---------------- ФУНКЦИИ ОТРИСОВКИ ----------------
def draw_main_menu():
    screen.fill(COLORS["bg"])
    
    # Заголовок с тенью
    title = font_huge.render("WAVE DEFENDER", True, COLORS["ui"])
    title_shadow = font_huge.render("WAVE DEFENDER", True, (0, 0, 0))
    screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 83))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    # Подзаголовок
    subtitle = font_medium.render("Defend against endless waves of enemies", True, (200, 200, 220))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 140))
    
    # Выбор уровня
    for i in range(len(LEVELS)):
        unlocked = i < unlocked_levels
        color = COLORS["button"] if unlocked else (80, 80, 80)
        hover_color = COLORS["button_hover"] if unlocked else (100, 100, 100)
        text_color = COLORS["text"] if unlocked else (120, 120, 120)
        
        rect = pygame.Rect(WIDTH//2 - 175, 200 + i * 85, 350, 70)
        
        # Эффект при наведении (только для ПК)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos) and unlocked and not IS_ANDROID
        
        pygame.draw.rect(screen, hover_color if is_hover else color, rect, 0, 15)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, 15)
        
        level_text = font_large.render(f"LEVEL {i+1}: {LEVELS[i]['name']}", True, text_color)
        screen.blit(level_text, level_text.get_rect(center=rect.center))
        
        # Информация об уровне
        info_text = font_small.render(f"Enemies: {LEVELS[i]['enemy_count']} | Waves: {LEVELS[i].get('waves', 3)}", 
                                     True, (180, 180, 200))
        screen.blit(info_text, (rect.centerx - info_text.get_width()//2, rect.bottom - 20))
        
        if not unlocked:
            lock_text = font_small.render("LOCKED - Complete previous level", True, (200, 200, 200))
            screen.blit(lock_text, (rect.centerx - lock_text.get_width()//2, rect.centery - 10))
    
    # Монеты и рекорд
    coin_text = font_large.render(f"Coins: {coins}", True, COLORS["coin"])
    screen.blit(coin_text, (30, 30))
    
    record_text = font_large.render(f"Best Wave: {best_wave}", True, COLORS["text"])
    screen.blit(record_text, (WIDTH - record_text.get_width() - 30, 30))
    
    # Управление (только для ПК)
    if not IS_ANDROID:
        controls_y = HEIGHT - 120
        controls = [
            "CONTROLS: A/D or ←/→ - Move | W/SPACE - Jump | B/Mouse Left - Shoot",
            "ESC - Pause/Menu | R - Restart level | F - Toggle auto-fire"
        ]
        for i, text in enumerate(controls):
            control_text = font_small.render(text, True, (180, 180, 200))
            screen.blit(control_text, (WIDTH//2 - control_text.get_width()//2, controls_y + i*20))
    
    # Кнопки внизу
    button_width = 200
    button_margin = 20
    
    # Кнопка магазина
    shop_rect = pygame.Rect(WIDTH//2 - button_width - button_margin//2, HEIGHT - 70, button_width, 50)
    shop_hover = shop_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
    pygame.draw.rect(screen, COLORS["button_hover"] if shop_hover else COLORS["button"], shop_rect, 0, 10)
    pygame.draw.rect(screen, (255, 255, 255), shop_rect, 2, 10)
    shop_text = font_medium.render("UPGRADES", True, (255, 255, 255))
    screen.blit(shop_text, shop_text.get_rect(center=shop_rect.center))
    
    # Кнопка выхода
    quit_rect = pygame.Rect(WIDTH//2 + button_margin//2, HEIGHT - 70, button_width, 50)
    quit_hover = quit_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
    pygame.draw.rect(screen, (200, 80, 80) if quit_hover else (180, 60, 60), quit_rect, 0, 10)
    pygame.draw.rect(screen, (255, 255, 255), quit_rect, 2, 10)
    quit_text = font_medium.render("QUIT", True, (255, 255, 255))
    screen.blit(quit_text, quit_text.get_rect(center=quit_rect.center))

def draw_game_ui():
    # Полоска здоровья
    health_width = 300 * SCALE_FACTOR
    health_percent = player.health / player.max_health
    health_color = COLORS["health"] if health_percent > 0.3 else (255, 50, 50)
    
    # Фон
    pygame.draw.rect(screen, (40, 40, 60), 
                    (20, 20, health_width, 25), 0, 5)
    # Полоска здоровья
    pygame.draw.rect(screen, health_color, 
                    (22, 22, (health_width - 4) * health_percent, 21), 0, 4)
    # Рамка
    pygame.draw.rect(screen, (255, 255, 255), 
                    (20, 20, health_width, 25), 2, 5)
    
    health_text = font_small.render(f"HP: {player.health:.1f}/{player.max_health}", True, COLORS["text"])
    screen.blit(health_text, (30, 50))
    
    # Прогресс уровня и волны
    wave_progress = wave_system.current_wave / max(1, wave_system.waves)
    wave_width = 400
    
    # Фон прогресса
    pygame.draw.rect(screen, (40, 40, 60), 
                    (WIDTH//2 - wave_width//2, 20, wave_width, 20), 0, 10)
    
    # Прогресс волны
    if wave_system.current_wave < wave_system.waves:
        enemies_left = max(0, wave_system.enemies_per_wave - len(enemies) - 
                          (wave_system.enemies_spawned_this_wave - len([e for e in enemies])))
        wave_fill = 1 - (enemies_left / wave_system.enemies_per_wave)
        pygame.draw.rect(screen, COLORS["wave_indicator"], 
                        (WIDTH//2 - wave_width//2 + 2, 22, 
                         (wave_width - 4) * wave_fill, 16), 0, 8)
    
    # Текст волны
    if wave_system.current_wave < wave_system.waves:
        wave_text = font_small.render(f"Wave {wave_system.current_wave + 1}/{wave_system.waves}", 
                                     True, COLORS["text"])
    else:
        wave_text = font_small.render("Final Wave - BOSS", True, COLORS["boss"])
    
    screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, 45))
    
    # Монеты
    coin_text = font_medium.render(f"Coins: {coins + coins_gained}", True, COLORS["coin"])
    screen.blit(coin_text, (WIDTH - coin_text.get_width() - 30, 25))
    
    # Автострельба индикатор
    if auto_shoot:
        auto_text = font_small.render("AUTO-FIRE: ON", True, (100, 255, 100))
        screen.blit(auto_text, (WIDTH - auto_text.get_width() - 30, 55))
    
    # Индикатор перезарядки
    if player.cooldown > 0:
        reload_width = 100 * (1 - player.cooldown / player.fire_rate)
        pygame.draw.rect(screen, (60, 60, 80), 
                        (WIDTH//2 - 50, HEIGHT - 40, 100, 10), 0, 5)
        pygame.draw.rect(screen, COLORS["bullet"], 
                        (WIDTH//2 - 48, HEIGHT - 38, reload_width * 0.96, 6), 0, 3)

def draw_upgrades_menu():
    screen.fill((30, 35, 60))
    
    title = font_huge.render("UPGRADES", True, COLORS["ui"])
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    
    coin_text = font_large.render(f"Coins: {coins}", True, COLORS["coin"])
    screen.blit(coin_text, (WIDTH//2 - coin_text.get_width()//2, 100))
    
    upgrades = [
        ("HEALTH", "Max HP +1", 100 + player_upgrades["health"] * 50, "health", 10),
        ("SPEED", "Move speed +25%", 120 + player_upgrades["speed"] * 60, "speed", 5),
        ("FIRE RATE", "Shoot faster", 150 + player_upgrades["fire_rate"] * 70, "fire_rate", 5),
        ("DAMAGE", "Bullet damage +75%", 200 + player_upgrades["damage"] * 80, "damage", 5),
        ("JUMP", "Jump height +20%", 80 + player_upgrades["jump"] * 40, "jump", 5),
        ("REGEN", "Health regen +0.5/sec", 300 + player_upgrades["regen"] * 150, "regen", 3)
    ]
    
    for i, (name, desc, price, key, max_level) in enumerate(upgrades):
        y = 150 + i * 85
        level = player_upgrades[key]
        maxed = level >= max_level
        
        # Фон улучшения
        rect = pygame.Rect(50, y, WIDTH - 100, 70)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos) and not maxed and not IS_ANDROID
        
        color = COLORS["button_hover"] if is_hover else COLORS["button"]
        if maxed:
            color = (80, 80, 80)
        elif coins < price:
            color = (100, 60, 60)
            
        pygame.draw.rect(screen, color, rect, 0, 10)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, 10)
        
        # Текст
        name_text = font_medium.render(f"{name} (Lvl {level}/{max_level})", True, COLORS["text"])
        screen.blit(name_text, (70, y + 15))
        
        desc_text = font_small.render(desc, True, (200, 200, 200))
        screen.blit(desc_text, (70, y + 40))
        
        # Цена
        if not maxed:
            price_text = font_medium.render(f"{price}", True, COLORS["coin"])
            screen.blit(price_text, (rect.right - 120, y + 25))
            
            # Кнопка покупки
            buy_rect = pygame.Rect(rect.right - 80, y + 20, 60, 30)
            can_afford = coins >= price
            btn_color = COLORS["button"] if can_afford else (120, 60, 60)
            btn_hover = buy_rect.collidepoint(mouse_pos) and can_afford and not IS_ANDROID
            
            pygame.draw.rect(screen, COLORS["button_hover"] if btn_hover else btn_color, buy_rect, 0, 5)
            buy_text = font_small.render("BUY" if can_afford else "POOR", True, (255, 255, 255))
            screen.blit(buy_text, buy_text.get_rect(center=buy_rect.center))
        else:
            max_text = font_medium.render("MAX LEVEL", True, (180, 180, 180))
            screen.blit(max_text, (rect.right - 100, y + 25))
    
    # Кнопка назад
    back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
    back_hover = back_rect.collidepoint(pygame.mouse.get_pos()) and not IS_ANDROID
    pygame.draw.rect(screen, COLORS["button_hover"] if back_hover else COLORS["button"], back_rect, 0, 10)
    back_text = font_medium.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))
    
    # Подсказка
    hint_text = font_small.render("Click on upgrades to purchase them", True, (180, 180, 200))
    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 120))

# ---------------- ГЛАВНЫЙ ЦИКЛ ----------------
running = True
mouse_pressed = False
mouse_pos = (0, 0)

while running:
    dt = clock.tick(FPS) / 1000.0
    
    # Обновление позиции мыши
    mouse_pos = pygame.mouse.get_pos()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            running = False
            
        # Мышь
        if event.type == pygame.MOUSEBUTTONDOWN and not IS_ANDROID:
            mouse_pressed = True
            
            if current_state == "GAME" and player:
                if event.button == 1:  # Левая кнопка мыши
                    new_bullets = player.shoot()
                    if new_bullets:
                        bullets.extend(new_bullets)
                        
            elif current_state == "MAIN_MENU":
                # Выбор уровня
                for i in range(len(LEVELS)):
                    rect = pygame.Rect(WIDTH//2 - 175, 200 + i * 85, 350, 70)
                    if rect.collidepoint(mouse_pos) and i < unlocked_levels:
                        init_game(i)
                        current_state = "GAME"
                        break
                
                # Кнопка магазина
                shop_rect = pygame.Rect(WIDTH//2 - 210, HEIGHT - 70, 200, 50)
                if shop_rect.collidepoint(mouse_pos):
                    current_state = "UPGRADES"
                    
                # Кнопка выхода
                quit_rect = pygame.Rect(WIDTH//2 + 10, HEIGHT - 70, 200, 50)
                if quit_rect.collidepoint(mouse_pos):
                    save_game()
                    running = False
                    
            elif current_state == "UPGRADES":
                # Покупка улучшений
                upgrades = [
                    ("health", 100 + player_upgrades["health"] * 50, 10),
                    ("speed", 120 + player_upgrades["speed"] * 60, 5),
                    ("fire_rate", 150 + player_upgrades["fire_rate"] * 70, 5),
                    ("damage", 200 + player_upgrades["damage"] * 80, 5),
                    ("jump", 80 + player_upgrades["jump"] * 40, 5),
                    ("regen", 300 + player_upgrades["regen"] * 150, 3)
                ]
                
                for i, (key, price, max_level) in enumerate(upgrades):
                    y = 150 + i * 85
                    rect = pygame.Rect(50, y, WIDTH - 100, 70)
                    buy_rect = pygame.Rect(rect.right - 80, y + 20, 60, 30)
                    
                    if buy_rect.collidepoint(mouse_pos) and player_upgrades[key] < max_level and coins >= price:
                        coins -= price
                        player_upgrades[key] += 1
                        if coin_sound:
                            coin_sound.play()
                        save_game()
                        # Обновляем игрока если он существует
                        if player:
                            player = Player(player_upgrades)
                
                # Кнопка назад
                back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
                if back_rect.collidepoint(mouse_pos):
                    current_state = "MAIN_MENU"
                    
            elif current_state in ["GAME_OVER", "LEVEL_COMPLETE"]:
                cont_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
                if cont_rect.collidepoint(mouse_pos):
                    current_state = "MAIN_MENU"
                    
        elif event.type == pygame.MOUSEBUTTONUP and not IS_ANDROID:
            mouse_pressed = False
            
        # Обработка касаний (Android)
        if IS_ANDROID and event.type == pygame.FINGERDOWN:
            x = event.x * WIDTH
            y = event.y * HEIGHT
            
            # Обновление виртуальных кнопок
            for btn in buttons.values():
                if btn.rect.collidepoint(x, y):
                    btn.pressed = True
                    
            if current_state == "MAIN_MENU":
                for i in range(len(LEVELS)):
                    rect = pygame.Rect(WIDTH//2 - 150, 200 + i * 70, 300, 50)
                    if rect.collidepoint(x, y) and i < unlocked_levels:
                        init_game(i)
                        current_state = "GAME"
                        break
                
                shop_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT - 80, 160, 50)
                if shop_rect.collidepoint(x, y):
                    current_state = "UPGRADES"
                    
            elif current_state == "UPGRADES":
                back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 80, 200, 50)
                if back_rect.collidepoint(x, y):
                    current_state = "MAIN_MENU"
                    
            elif current_state in ["GAME_OVER", "LEVEL_COMPLETE"]:
                cont_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 60)
                if cont_rect.collidepoint(x, y):
                    current_state = "MAIN_MENU"
                    
        elif IS_ANDROID and event.type == pygame.FINGERUP:
            for btn in buttons.values():
                btn.pressed = False
        
        # Клавиатура (PC)
        if event.type == pygame.KEYDOWN:
            if current_state == "MAIN_MENU":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    level_idx = event.key - pygame.K_1
                    if level_idx < unlocked_levels:
                        init_game(level_idx)
                        current_state = "GAME"
                elif event.key == pygame.K_u:
                    current_state = "UPGRADES"
                elif event.key == pygame.K_ESCAPE:
                    save_game()
                    running = False
                    
            elif current_state == "GAME":
                if event.key == pygame.K_ESCAPE:
                    current_state = "MAIN_MENU"
                elif event.key == pygame.K_b and player:
                    new_bullets = player.shoot()
                    if new_bullets:
                        bullets.extend(new_bullets)
                elif event.key == pygame.K_r:  # Рестарт уровня
                    init_game(current_level)
                elif event.key == pygame.K_f:  # Переключение автострельбы
                    auto_shoot = not auto_shoot
                elif event.key == pygame.K_p:  # Пауза
                    current_state = "PAUSE"
                    
            elif current_state == "PAUSE":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    current_state = "GAME"
                    
            elif current_state == "UPGRADES":
                if event.key == pygame.K_ESCAPE:
                    current_state = "MAIN_MENU"
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                    idx = event.key - pygame.K_1
                    keys = ["health", "speed", "fire_rate", "damage", "jump", "regen"]
                    max_levels = [10, 5, 5, 5, 5, 3]
                    
                    if idx < len(keys):
                        key = keys[idx]
                        price = [100 + player_upgrades["health"] * 50,
                                120 + player_upgrades["speed"] * 60,
                                150 + player_upgrades["fire_rate"] * 70,
                                200 + player_upgrades["damage"] * 80,
                                80 + player_upgrades["jump"] * 40,
                                300 + player_upgrades["regen"] * 150][idx]
                        
                        if player_upgrades[key] < max_levels[idx] and coins >= price:
                            coins -= price
                            player_upgrades[key] += 1
                            if coin_sound:
                                coin_sound.play()
                            save_game()
                            if player:
                                player = Player(player_upgrades)
                            
            elif current_state in ["GAME_OVER", "LEVEL_COMPLETE"]:
                if event.key in [pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE]:
                    current_state = "MAIN_MENU"
    
    # Автострельба
    if auto_shoot and current_state == "GAME" and player:
        auto_shoot_timer += 1
        if auto_shoot_timer >= player.fire_rate:
            new_bullets = player.shoot()
            if new_bullets:
                bullets.extend(new_bullets)
            auto_shoot_timer = 0
    
    # Обновление состояний игры
    if current_state == "GAME" and player:
        keys = pygame.key.get_pressed()
        touch_input = None
        
        # Управление на Android
        if IS_ANDROID:
            touch_input = {
                'left': buttons['left'].pressed,
                'right': buttons['right'].pressed,
                'jump': buttons['jump'].pressed,
                'shoot': buttons['shoot'].pressed
            }
            
            # Стрельба на Android
            if touch_input.get('shoot'):
                new_bullets = player.shoot()
                if new_bullets:
                    bullets.extend(new_bullets)
        
        # Движение игрока
        player.move(keys, touch_input)
        
        # Обновление системы волн
        wave_system.update()
        
        # Спавн врагов
        level_data = LEVELS[current_level]
        spawn_timer += dt * 1000
        
        if wave_system.should_spawn() and spawn_timer > level_data["spawn_rate"]:
            # Проверка на босса (последний враг последней волны)
            is_boss = False
            if level_data["boss"] and wave_system.current_wave == wave_system.waves - 1:
                if wave_system.enemies_spawned_this_wave == wave_system.enemies_per_wave - 1:
                    is_boss = True
            
            enemy = wave_system.spawn_enemy(level_data, current_level, is_boss)
            enemies.append(enemy)
            spawn_timer = 0
            
            if is_boss:
                effects.append(Effect(WIDTH//2, 150, "!!! BOSS INCOMING !!!", COLORS["boss"], 90))
                shake_timer = 30
        
        # Обновление пуль
        for bullet in bullets[:]:
            if bullet.update():
                bullets.remove(bullet)
                continue
                
            # Проверка столкновений с врагами
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if enemy.take_damage(bullet.damage):
                        # Убийство врага
                        enemies.remove(enemy)
                        coins_gained += enemy.value
                        effects.append(Effect(enemy.rect.centerx, enemy.rect.top, 
                                            f"+{enemy.value}", COLORS["coin"], 45))
                        
                        # Бонус за босса
                        if enemy.is_boss:
                            coins_gained += 200
                            effects.append(Effect(WIDTH//2, HEIGHT//2, 
                                                "BOSS DEFEATED! +200", COLORS["coin"], 120))
                            shake_timer = 20
                        
                        if hit_sound:
                            hit_sound.play()
                    bullets.remove(bullet)
                    break
        
        # Обновление врагов и их снарядов
        for enemy in enemies[:]:
            if enemy.update():
                enemies.remove(enemy)
                continue
                
            # Обновление снарядов босса
            for proj in enemy.projectiles[:]:
                if proj.update():
                    enemy.projectiles.remove(proj)
                
            # Столкновение с игроком
            if player.rect.colliderect(enemy.rect):
                damage = 2 if enemy.is_boss else 1
                if player.take_damage(damage):
                    effects.append(Effect(player.rect.centerx, player.rect.top, 
                                        f"-{damage}", COLORS["health"], 30))
                    shake_timer = 15
                    
                    if player.health <= 0:
                        current_state = "GAME_OVER"
                        coins += coins_gained
                        if current_level + 1 > best_wave:
                            best_wave = current_level + 1
                        save_game()
        
        # Обновление эффектов
        for effect in effects[:]:
            if effect.update():
                effects.remove(effect)
        
        # Проверка завершения уровня
        if (wave_system.current_wave >= wave_system.waves and 
            len(enemies) == 0 and not level_complete):
            level_complete = True
            coins += coins_gained
            
            # Разблокировка следующего уровня
            if current_level + 1 == unlocked_levels and current_level + 1 < len(LEVELS):
                unlocked_levels += 1
            
            if level_up_sound:
                level_up_sound.play()
                
            current_state = "LEVEL_COMPLETE"
            save_game()
    
    # Дрожание камеры
    shake_x = shake_y = 0
    if shake_timer > 0:
        shake_timer -= 1
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-3, 3)
    
    # Отрисовка
    screen.fill((0, 0, 0))
    
    if current_state == "MAIN_MENU":
        draw_main_menu()
        
    elif current_state == "UPGRADES":
        draw_upgrades_menu()
        
    elif current_state == "GAME" and player:
        # Фон уровня
        level_color = LEVELS[current_level]["bg_color"]
        screen.fill(level_color)
        
        # Декоративные элементы
        for i in range(20):
            x = (i * 100) % WIDTH
            y = HEIGHT - 40 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 5
            pygame.draw.line(screen, (COLORS["platform"][0]//2, COLORS["platform"][1]//2, COLORS["platform"][2]//2),
                           (x, y), (x + 50, y), 3)
        
        # Платформа
        pygame.draw.rect(screen, COLORS["platform"], 
                        (0, HEIGHT - 30, WIDTH, 30))
        
        # Текстура платформы
        for i in range(0, WIDTH, 30):
            pygame.draw.line(screen, (COLORS["platform"][0]+20, COLORS["platform"][1]+20, COLORS["platform"][2]+20),
                           (i, HEIGHT - 30), (i, HEIGHT), 2)
        
        # Игровые объекты
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()
        player.draw()
        for effect in effects:
            effect.draw()
        
        draw_game_ui()
        
        # Виртуальные кнопки (Android)
        if IS_ANDROID:
            for btn in buttons.values():
                btn.draw(screen)
                
        # Отображение волны
        if wave_system.wave_cooldown > 0:
            wave_text = font_large.render(f"Next wave in: {wave_system.wave_cooldown//60 + 1}", 
                                         True, COLORS["wave_indicator"])
            screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, HEIGHT//2 - 50))
            
    elif current_state == "PAUSE":
        # Полупрозрачный фон
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        pause_text = font_huge.render("PAUSED", True, COLORS["ui"])
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        
        continue_text = font_medium.render("Press P or ESC to continue", True, COLORS["text"])
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
        
        menu_text = font_small.render("Press ESC again for main menu", True, (200, 200, 200))
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 60))
                
    elif current_state == "LEVEL_COMPLETE":
        screen.fill(LEVELS[current_level]["bg_color"])
        
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        success_text = font_huge.render("LEVEL COMPLETE!", True, COLORS["coin"])
        screen.blit(success_text, (WIDTH//2 - success_text.get_width()//2, 100))
        
        coin_text = font_large.render(f"Coins earned: +{coins_gained}", True, COLORS["coin"])
        screen.blit(coin_text, (WIDTH//2 - coin_text.get_width()//2, 180))
        
        if current_level + 1 < len(LEVELS):
            next_text = font_medium.render(f"Next: {LEVELS[current_level + 1]['name']}", 
                                          True, COLORS["text"])
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, 240))
        else:
            final_text = font_medium.render("All levels completed! Congratulations!", 
                                           True, COLORS["wave_indicator"])
            screen.blit(final_text, (WIDTH//2 - final_text.get_width()//2, 240))
        
        # Кнопка продолжения
        cont_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 200, 60)
        cont_hover = cont_rect.collidepoint(mouse_pos) and not IS_ANDROID
        pygame.draw.rect(screen, COLORS["button_hover"] if cont_hover else COLORS["button"], cont_rect, 0, 10)
        cont_text = font_medium.render("CONTINUE", True, (255, 255, 255))
        screen.blit(cont_text, cont_text.get_rect(center=cont_rect.center))
        
        # Статистика
        stats_y = 300
        stats = [
            f"Enemies defeated: {LEVELS[current_level]['enemy_count']}",
            f"Waves survived: {LEVELS[current_level].get('waves', 3)}",
            f"Total coins: {coins}",
            f"Best wave: {best_wave}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, (220, 220, 220))
            screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, stats_y + i * 30))
        
    elif current_state == "GAME_OVER":
        screen.fill((40, 20, 30))
        
        # Затемнение
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        over_text = font_huge.render("GAME OVER", True, COLORS["health"])
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, 100))
        
        wave_text = font_large.render(f"Reached Level: {current_level + 1}", 
                                     True, COLORS["text"])
        screen.blit(wave_text, (WIDTH//2 - wave_text.get_width()//2, 180))
        
        coin_text = font_medium.render(f"Coins earned this run: +{coins_gained}", 
                                      True, COLORS["coin"])
        screen.blit(coin_text, (WIDTH//2 - coin_text.get_width()//2, 240))
        
        # Кнопка продолжения
        cont_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 200, 60)
        cont_hover = cont_rect.collidepoint(mouse_pos) and not IS_ANDROID
        pygame.draw.rect(screen, COLORS["button_hover"] if cont_hover else COLORS["button"], cont_rect, 0, 10)
        cont_text = font_medium.render("MAIN MENU", True, (255, 255, 255))
        screen.blit(cont_text, cont_text.get_rect(center=cont_rect.center))
        
        # Подсказка
        hint_text = font_small.render("Upgrade your character to progress further!", True, (220, 180, 180))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 80))
    
    # Применение дрожания
    if shake_x != 0 or shake_y != 0:
        shaken_surface = pygame.Surface((WIDTH, HEIGHT))
        shaken_surface.blit(screen, (shake_x, shake_y))
        screen.blit(shaken_surface, (0, 0))
    
    # Курсор мыши (только для ПК)
    if not IS_ANDROID and current_state in ["MAIN_MENU", "UPGRADES", "LEVEL_COMPLETE", "GAME_OVER"]:
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, 5)
        pygame.draw.circle(screen, (0, 0, 0), mouse_pos, 5, 1)
    
    pygame.display.flip()

pygame.quit()
sys.exit()