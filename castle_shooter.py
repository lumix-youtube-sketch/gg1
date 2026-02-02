"""
Castle Shooter - игра на библиотеке Arcade
Исправленная версия
"""

import arcade
import math
import random

# Настройки экрана
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Castle Shooter"
FPS = 60
TILE_SIZE = 50

# Цвета
BLACK = (10, 10, 10)
FLOOR_COLOR = (40, 30, 30)
WALL_COLOR = (80, 60, 60)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
PURPLE = (150, 50, 200)
YELLOW = (255, 255, 0)
PORTAL_COLOR = (0, 255, 255)
GOLD = (255, 215, 0)
DARK_RED = (100, 20, 20)
STONE = (120, 100, 80)

# Карты уровней
MAP1 = [
    "#########################################################",
    "#............#.................................#........#",
    "#....P.......#.............................w...#....n...#",
    "#............#.................................#........#",
    "#............#..w..#....................########........#",
    "#............#.....#....................................#",
    "#............#######....................................#",
    "#..........................#...........n................#",
    "#..........................#...................####.....#",
    "#..........................#...................#........#",
    "##############.........n...#...................#........#",
    "#..........................#...................#....w...#",
    "#..........................#......w............#........#",
    "#...............############...........##################",
    "#...............#.......................................#",
    "#...............#.....w.................................#",
    "#...............#...................................n...#",
    "#...............#.......................................#",
    "#...............###########.............................#",
    "#...................................##############......#",
    "#....n.....................................#............#",
    "#..........................................#............#",
    "#.............................#............#......N.....#",
    "#.................w...........#.......w....#............#",
    "#.............................#............#............#",
    "#########################################################"
]

MAP2 = [
    "#########################################################",
    "#.......................................................#",
    "#...............n..............w..................P.....#",
    "#.......................................................#",
    "#.......................................................#",
    "#....w......#############################################",
    "#.......................................................#",
    "#...................n...............w...................#",
    "#.......................................................#",
    "###############################................w........#",
    "#.......................................................#",
    "#...........w..............n............................#",
    "#.......................................................#",
    "#.................................#######################",
    "#.......................................................#",
    "#............n.............................w............#",
    "#.......................................................#",
    "##################################################......#",
    "#...........#...........................................#",
    "#...........#...........................................#",
    "#.......................................................#",
    "#........................B..............................#",
    "#.......................................................#",
    "#...........#...........................................#",
    "#...........#...........................................#",
    "#########################################################"
]


class Corpse(arcade.Sprite):
    """Труп врага"""

    def __init__(self, x, y, kind):
        super().__init__()

        if kind == "weak":
            size = 35
        elif kind == "norm":
            size = 40
        else:
            size = 80

        self.texture = arcade.make_soft_square_texture(size, RED, 255, 255)
        self.center_x = x
        self.center_y = y
        self.lifetime = 300

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()
        if self.lifetime < 60:
            self.alpha = int((self.lifetime / 60) * 255)


class Wall(arcade.Sprite):
    """Стена"""

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_square_texture(TILE_SIZE, WALL_COLOR, 255, 255)
        self.center_x = x
        self.center_y = y


class Portal(arcade.Sprite):
    """Портал на следующий уровень"""

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(TILE_SIZE, PORTAL_COLOR, 255, 255)
        self.center_x = x
        self.center_y = y


class Bullet(arcade.Sprite):
    """Пуля"""

    def __init__(self, x, y, angle, is_player=True):
        super().__init__()

        self.is_player = is_player

        if is_player:
            self.speed = 10
            self.damage = 25
            self.texture = arcade.make_soft_circle_texture(15, YELLOW, 255, 255)
        else:
            self.speed = 6
            self.damage = 15
            self.texture = arcade.make_soft_circle_texture(20, RED, 255, 255)

        self.center_x = x
        self.center_y = y
        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed
        self.lifetime = 50

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class Player(arcade.Sprite):
    """Игрок"""

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_soft_circle_texture(40, GREEN, 255, 255)
        self.center_x = x
        self.center_y = y
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.last_shot = 0

        # Флаги движения
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

    def update(self):
        dx = 0
        dy = 0

        if self.up_pressed:
            dy = self.speed
        if self.down_pressed:
            dy = -self.speed
        if self.left_pressed:
            dx = -self.speed
        if self.right_pressed:
            dx = self.speed

        # Диагональное движение
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.center_x += dx
        self.center_y += dy


class Enemy(arcade.Sprite):
    """Враг"""

    def __init__(self, x, y, kind):
        super().__init__()

        self.kind = kind
        self.player = None
        self.aggro = False
        self.aggro_range = 200

        if kind == "weak":
            self.hp = 30
            self.max_hp = 30
            self.speed = 3
            self.texture = arcade.make_soft_circle_texture(50, PURPLE, 255, 255)
        elif kind == "norm":
            self.hp = 60
            self.max_hp = 60
            self.speed = 2
            self.texture = arcade.make_soft_square_texture(70, PURPLE, 255, 255)
        elif kind == "boss":
            self.hp = 300
            self.max_hp = 300
            self.speed = 2
            self.aggro_range = 350
            self.texture = arcade.make_soft_circle_texture(125, (150, 0, 150), 255, 255)

        self.center_x = x
        self.center_y = y
        self.last_shot = 0

    def update(self):
        if not self.player:
            return

        dx = self.player.center_x - self.center_x
        dy = self.player.center_y - self.center_y
        dist = math.hypot(dx, dy)

        if dist < self.aggro_range:
            self.aggro = True

        if not self.aggro:
            return

        if dist > 50:
            if dist != 0:
                dx = (dx / dist) * self.speed
                dy = (dy / dist) * self.speed
                self.center_x += dx
                self.center_y += dy


class CastleShooter(arcade.Window):
    """Главный класс игры"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BLACK)

        self.game_state = "MENU"

        # Списки спрайтов
        self.all_sprites = None
        self.wall_list = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.enemy_list = None
        self.portal_list = None
        self.corpse_list = None

        self.player = None
        self.current_level = 1

        # Камеры
        self.camera = None
        self.gui_camera = None

        # Мышь
        self.mouse_x = 0
        self.mouse_y = 0

        # Флаги для звуков
        self.game_over_played = False
        self.victory_played = False

    def setup(self):
        """Настройка игры"""
        # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
        # Используем обычную arcade.Camera вместо Camera2D
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.gui_camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        # -------------------------

        self.all_sprites = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.corpse_list = arcade.SpriteList()

        self.load_level(self.current_level)

    def load_level(self, level_num):
        """Загрузка уровня"""
        self.all_sprites = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.corpse_list = arcade.SpriteList()

        current_map = MAP1 if level_num == 1 else MAP2

        for row_idx, row in enumerate(current_map):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE + TILE_SIZE // 2
                y = (len(current_map) - row_idx - 1) * TILE_SIZE + TILE_SIZE // 2

                if char == "#":
                    wall = Wall(x, y)
                    self.wall_list.append(wall)
                    self.all_sprites.append(wall)
                elif char == "P":
                    self.player = Player(x, y)
                    self.all_sprites.append(self.player)
                elif char == "w":
                    enemy = Enemy(x, y, "weak")
                    self.enemy_list.append(enemy)
                    self.all_sprites.append(enemy)
                elif char == "n":
                    enemy = Enemy(x, y, "norm")
                    self.enemy_list.append(enemy)
                    self.all_sprites.append(enemy)
                elif char == "B":
                    enemy = Enemy(x, y, "boss")
                    self.enemy_list.append(enemy)
                    self.all_sprites.append(enemy)
                elif char == "N":
                    portal = Portal(x, y)
                    self.portal_list.append(portal)
                    self.all_sprites.append(portal)

        for enemy in self.enemy_list:
            enemy.player = self.player

    def on_draw(self):
        """Рисование"""
        self.clear()

        if self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state in ["GAME", "GAME_OVER", "VICTORY"]:
            self.draw_game()

    def draw_menu(self):
        """Рисуем меню"""
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (20, 15, 10))

        arcade.draw_text("CASTLE SHOOTERS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150,
                         GOLD, 72, anchor_x="center", bold=True)

        # Кнопка старта
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     300, 70, DARK_RED)
        arcade.draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      300, 70, GOLD, 4)
        arcade.draw_text("START GAME", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10,
                         GOLD, 32, anchor_x="center", bold=True)

        # Кнопка выхода
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                                     300, 70, (60, 30, 30))
        arcade.draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                                      300, 70, GOLD, 4)
        arcade.draw_text("LEAVE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 110,
                         GOLD, 32, anchor_x="center", bold=True)

    def draw_game(self):
        """Рисуем игру"""
        self.camera.use()

        # Пол
        arcade.draw_lrtb_rectangle_filled(0, len(MAP1[0]) * TILE_SIZE,
                                          len(MAP1) * TILE_SIZE, 0, FLOOR_COLOR)

        # Спрайты
        self.wall_list.draw()
        self.portal_list.draw()
        self.corpse_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()

        if self.player:
            self.player.draw()

        # Здоровье врагов
        for enemy in self.enemy_list:
            if enemy.hp < enemy.max_hp:
                self.draw_health_bar(enemy.center_x, enemy.top + 10,
                                     enemy.hp, enemy.max_hp, 50)

        self.gui_camera.use()

        # Интерфейс
        if self.player:
            self.draw_health_bar(110, SCREEN_HEIGHT - 30,
                                 self.player.hp, 100, 200)

            arcade.draw_text(f"HP: {self.player.hp}/100",
                             10, SCREEN_HEIGHT - 65, WHITE, 20)
            arcade.draw_text(f"Enemies left: {len(self.enemy_list)}",
                             10, SCREEN_HEIGHT - 90, WHITE, 20)
            arcade.draw_text(f"Current level: {self.current_level}",
                             10, SCREEN_HEIGHT - 115, WHITE, 20)

        if self.game_state == "GAME_OVER":
            arcade.draw_text("DEFEAT", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             RED, 72, anchor_x="center", bold=True)
            arcade.draw_text("Press SPACE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70,
                             WHITE, 32, anchor_x="center", bold=True)

        if self.game_state == "VICTORY":
            arcade.draw_text("VICTORY!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             GOLD, 72, anchor_x="center", bold=True)
            arcade.draw_text("Press SPACE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70,
                             WHITE, 32, anchor_x="center", bold=True)

    def draw_health_bar(self, x, y, hp, max_hp, width):
        """Полоска здоровья"""
        ratio = max(0, hp / max_hp)
        fill = int(width * ratio)

        if ratio > 0.6:
            color = GREEN
        elif ratio > 0.3:
            color = YELLOW
        else:
            color = RED

        arcade.draw_rectangle_filled(x, y, fill, 20, color)
        arcade.draw_rectangle_outline(x, y, width, 20, WHITE, 2)

    def on_update(self, delta_time):
        """Обновление логики"""
        if self.game_state != "GAME":
            return

        if self.player:
            self.player.update()

            # Столкновения со стенами
            walls_hit = arcade.check_for_collision_with_list(self.player, self.wall_list)
            if walls_hit:
                self.player.center_x -= self.player.change_x * 2
                self.player.center_y -= self.player.change_y * 2

        # Враги
        self.enemy_list.update()

        # Стрельба врагов
        for enemy in self.enemy_list:
            if enemy.aggro and self.player:
                now = arcade.get_time()
                delay = 1.2 if enemy.kind != "boss" else 0.6

                if now - enemy.last_shot > delay:
                    enemy.last_shot = now
                    angle = math.atan2(
                        self.player.center_y - enemy.center_y,
                        self.player.center_x - enemy.center_x
                    )
                    bullet = Bullet(enemy.center_x, enemy.center_y, angle, False)
                    self.enemy_bullet_list.append(bullet)
                    self.all_sprites.append(bullet)

        # Пули
        self.bullet_list.update()
        self.enemy_bullet_list.update()

        # Пули врезаются в стены
        for bullet in self.bullet_list:
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()

        for bullet in self.enemy_bullet_list:
            if arcade.check_for_collision_with_list(bullet, self.wall_list):
                bullet.remove_from_sprite_lists()

        # Попадания по врагам
        for bullet in self.bullet_list:
            enemies_hit = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            for enemy in enemies_hit:
                enemy.hp -= bullet.damage
                enemy.aggro = True
                bullet.remove_from_sprite_lists()

                if enemy.hp <= 0:
                    corpse = Corpse(enemy.center_x, enemy.center_y, enemy.kind)
                    self.corpse_list.append(corpse)
                    enemy.remove_from_sprite_lists()

        # Попадания по игроку
        if self.player:
            bullets_hit = arcade.check_for_collision_with_list(
                self.player, self.enemy_bullet_list
            )
            for bullet in bullets_hit:
                self.player.hp -= bullet.damage
                bullet.remove_from_sprite_lists()

            if self.player.hp <= 0:
                self.game_state = "GAME_OVER"
                if not self.game_over_played:
                    self.game_over_played = True

        # Трупы
        self.corpse_list.update()

        # Портал
        if self.current_level == 1 and self.player:
            if arcade.check_for_collision_with_list(self.player, self.portal_list):
                if len(self.enemy_list) == 0:
                    self.current_level = 2
                    self.load_level(2)

        # Победа
        if self.current_level == 2 and len(self.enemy_list) == 0:
            self.game_state = "VICTORY"
            if not self.victory_played:
                self.victory_played = True

        # Камера
        if self.player:
            self.center_camera()

    def center_camera(self):
        """Центрируем камеру"""
        screen_center_x = self.player.center_x - (SCREEN_WIDTH / 2)
        screen_center_y = self.player.center_y - (SCREEN_HEIGHT / 2)

        screen_center_x = max(0, screen_center_x)
        screen_center_y = max(0, screen_center_y)

        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered, 0.15)

    def on_mouse_press(self, x, y, button, modifiers):
        """Нажатие мыши"""
        if self.game_state == "MENU":
            # Проверка кнопок
            if (SCREEN_WIDTH // 2 - 150 < x < SCREEN_WIDTH // 2 + 150 and
                    SCREEN_HEIGHT // 2 - 35 < y < SCREEN_HEIGHT // 2 + 35):
                self.game_state = "GAME"
                self.setup()
            elif (SCREEN_WIDTH // 2 - 150 < x < SCREEN_WIDTH // 2 + 150 and
                  SCREEN_HEIGHT // 2 - 135 < y < SCREEN_HEIGHT // 2 - 65):
                arcade.close_window()

        elif self.game_state == "GAME":
            if self.player and button == arcade.MOUSE_BUTTON_LEFT:
                now = arcade.get_time()
                if now - self.player.last_shot > 0.75:
                    self.player.last_shot = now

                    world_x = x + self.camera.position[0]
                    world_y = y + self.camera.position[1]

                    angle = math.atan2(
                        world_y - self.player.center_y,
                        world_x - self.player.center_x
                    )

                    bullet = Bullet(self.player.center_x, self.player.center_y,
                                    angle, True)
                    self.bullet_list.append(bullet)
                    self.all_sprites.append(bullet)

    def on_key_press(self, key, modifiers):
        """Нажатие клавиши"""
        if key == arcade.key.ESCAPE:
            if self.game_state == "GAME":
                self.game_state = "MENU"
            else:
                arcade.close_window()

        if key == arcade.key.SPACE:
            if self.game_state in ["GAME_OVER", "VICTORY"]:
                self.game_state = "MENU"
                self.current_level = 1
                self.game_over_played = False
                self.victory_played = False

        if self.game_state == "GAME" and self.player:
            if key in [arcade.key.W, arcade.key.UP]:
                self.player.up_pressed = True
            elif key in [arcade.key.S, arcade.key.DOWN]:
                self.player.down_pressed = True
            elif key in [arcade.key.A, arcade.key.LEFT]:
                self.player.left_pressed = True
            elif key in [arcade.key.D, arcade.key.RIGHT]:
                self.player.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Отпускание клавиши"""
        if self.game_state == "GAME" and self.player:
            if key in [arcade.key.W, arcade.key.UP]:
                self.player.up_pressed = False
            elif key in [arcade.key.S, arcade.key.DOWN]:
                self.player.down_pressed = False
            elif key in [arcade.key.A, arcade.key.LEFT]:
                self.player.left_pressed = False
            elif key in [arcade.key.D, arcade.key.RIGHT]:
                self.player.right_pressed = False


def main():
    """Запуск игры"""
    game = CastleShooter()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()