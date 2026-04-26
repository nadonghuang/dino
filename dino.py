#!/usr/bin/env python3
"""
dino - 🦕 Chrome Dinosaur Game in Your Terminal

The classic T-Rex runner game, reborn in your terminal.
Pure Python, zero dependencies — just run and jump!

Usage:
    python dino.py

Controls:
    SPACE / UP   — Jump
    DOWN         — Duck
    Any key      — Restart (after game over)
    Q / ESC      — Quit
"""

import curses
import random
import time
import sys
import os

# ══════════════════════════════════════════════════════════════
# 配置常量
# ══════════════════════════════════════════════════════════════

# 物理参数
GRAVITY = 0.6
JUMP_VELOCITY = -2.8
DUCK_HEIGHT_REDUCTION = 3  # 蹲下时碰撞箱高度减少

# 游戏参数
INITIAL_SPEED = 8          # 初始速度 (字符/秒)
MAX_SPEED = 25
SPEED_INCREMENT = 0.002    # 每帧速度增加
NIGHT_CYCLE = 700          # 每多少分切换日夜
MIN_OBSTACLE_GAP = 15      # 障碍物最小间距

# 帧率
TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS

# ══════════════════════════════════════════════════════════════
# ASCII 精灵图
# ══════════════════════════════════════════════════════════════

# 恐龙 — 跑步帧1 (6宽 × 7高)
DINO_RUN_1 = [
    "  ▄█▄ ",
    " ▄███ ",
    " █████",
    " █████",
    "  ▀▀▀▀",
    "  ▀▄ ▀",
    "  ▀   ",
]

# 恐龙 — 跑步帧2 (6宽 × 7高)
DINO_RUN_2 = [
    "  ▄█▄ ",
    " ▄███ ",
    " █████",
    " █████",
    "  ▀▀▀▀",
    "  ▀ ▄▀",
    "    ▀ ",
]

# 恐龙 — 站立/跳跃 (6宽 × 7高)
DINO_STAND = [
    "  ▄█▄ ",
    " ▄███ ",
    " █████",
    " █████",
    "  ▀▀▀▀",
    "  ▀▀▀▀",
    "      ",
]

# 恐龙 — 蹲下帧1 (8宽 × 4高)
DINO_DUCK_1 = [
    "   ▄█▄   ",
    "▄███████ ",
    "▀▀▀▀▀▀▀▀▄",
    "  ▀▄  ▀  ",
]

# 恐龙 — 蹲下帧2 (8宽 × 4高)
DINO_DUCK_2 = [
    "   ▄█▄   ",
    "▄███████ ",
    "▀▀▀▀▀▀▀▀▄",
    "   ▀  ▄▀ ",
]

# 恐龙 — 死亡 (6宽 × 7高)
DINO_DEAD = [
    "  ▄█▄ ",
    " ▄███ ",
    "█ █████",
    " █████",
    "  ▀▀▀▀",
    "  ▀▀▀▀",
    "      ",
]

# 小仙人掌 (3宽 × 5高)
CACTUS_SMALL = [
    " ▄ ",
    "▄█▄",
    "███",
    " █ ",
    " █ ",
]

# 大仙人掌 (5宽 × 7高)
CACTUS_LARGE = [
    " ▄▄▄ ",
    "▄█ █▄",
    "█████",
    " ███ ",
    "  █  ",
    "  █  ",
    "  █  ",
]

# 双仙人掌 (6宽 × 5高)
CACTUS_DOUBLE = [
    "▄  ▄ ",
    "██ ██",
    "█████",
    " █ █ ",
    " █ █ ",
]

# 翼龙帧1 — 翅膀上 (7宽 × 3高)
PTERO_1 = [
    "  ▄▄▄  ",
    "▄█████▄",
    "  ▀  ▀ ",
]

# 翼龙帧2 — 翅膀下 (7宽 × 3高)
PTERO_2 = [
    "  ▄  ▄ ",
    "▄█████▄",
    "  ▀▀▀  ",
]

# 云朵 (7宽 × 2高)
CLOUD = [
    "  ▄▄▄▄ ",
    "▄▀   ▀▄",
]

# 星星
STARS = ["✦", "✧", "⋆", "·"]

# 地面纹理
GROUND_CHARS = "·․⋅∙"


# ══════════════════════════════════════════════════════════════
# 碰撞箱定义
# ══════════════════════════════════════════════════════════════

def get_hitbox(sprite, x, y):
    """获取精灵的紧凑碰撞箱 (去除空白行列)"""
    if not sprite:
        return (x, y, 0, 0)
    # 找到实际内容的边界
    min_col = len(sprite[0]) if sprite else 0
    max_col = 0
    min_row = len(sprite)
    max_row = 0
    for r, row in enumerate(sprite):
        for c, ch in enumerate(row):
            if ch != ' ':
                min_col = min(min_col, c)
                max_col = max(max_col, c)
                min_row = min(min_row, r)
                max_row = max(max_row, r)
    # 缩小碰撞箱以增加容错
    pad = 1
    x1 = x + min_col + pad
    y1 = y + min_row + pad
    x2 = x + max_col - pad + 1
    y2 = y + max_row - pad + 1
    return (x1, y1, x2, y2)


def boxes_overlap(a, b):
    """检测两个碰撞箱是否重叠"""
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


# ══════════════════════════════════════════════════════════════
# 游戏对象
# ══════════════════════════════════════════════════════════════

class Player:
    """霸王龙玩家"""

    def __init__(self, ground_y):
        self.x = 8                    # 水平位置 (固定)
        self.ground_y = ground_y      # 地面Y坐标
        self.y_offset = 0.0           # 跳跃偏移 (像素, 向上为负)
        self.vy = 0.0                 # 垂直速度
        self.ducking = False
        self.frame_counter = 0
        self.frame = 0

    @property
    def screen_y(self):
        """恐龙顶部在屏幕上的Y坐标"""
        base_y = self.ground_y - self.sprite_height
        return base_y + int(self.y_offset)

    @property
    def sprite(self):
        if self.ducking:
            return [DINO_DUCK_1, DINO_DUCK_2][self.frame % 2]
        if self.y_offset < 0:
            return DINO_STAND
        return [DINO_RUN_1, DINO_RUN_2][self.frame % 2]

    @property
    def sprite_height(self):
        return len(self.sprite)

    @property
    def sprite_width(self):
        return max(len(row) for row in self.sprite)

    def jump(self):
        """跳跃 (仅在地面时)"""
        if self.y_offset >= 0:
            self.vy = JUMP_VELOCITY
            self.ducking = False

    def duck(self, active):
        """蹲下"""
        if self.y_offset >= 0:
            self.ducking = active
            if active:
                self.vy = 0
                self.y_offset = 0

    def update(self):
        """更新物理状态"""
        # 重力
        if self.y_offset < 0:
            self.vy += GRAVITY
            self.y_offset += self.vy
        else:
            self.y_offset = 0
            self.vy = 0

        # 动画帧
        self.frame_counter += 1
        if self.frame_counter >= 6:
            self.frame_counter = 0
            self.frame += 1

    def get_hitbox(self):
        """获取碰撞箱"""
        return get_hitbox(self.sprite, self.x, self.screen_y)


class Obstacle:
    """障碍物"""

    TYPES = {
        'small':  CACTUS_SMALL,
        'large':  CACTUS_LARGE,
        'double': CACTUS_DOUBLE,
        'ptero':  None,  # 翼龙有动画，特殊处理
    }

    def __init__(self, x, ground_y, kind, speed):
        self.x = float(x)
        self.kind = kind
        self.ground_y = ground_y
        self.frame = 0
        self.frame_counter = 0

        # 翼龙飞行高度 (地面以上3-5行)
        if kind == 'ptero':
            heights = [ground_y - 4, ground_y - 7, ground_y - 10]
            self.y = random.choice(heights)
        else:
            self.y = ground_y - self.sprite_height

    @property
    def sprite(self):
        if self.kind == 'ptero':
            return [PTERO_1, PTERO_2][self.frame % 2]
        return self.TYPES[self.kind]

    @property
    def sprite_height(self):
        return len(self.sprite)

    @property
    def sprite_width(self):
        return max(len(row) for row in self.sprite)

    def update(self, speed):
        """向左移动"""
        self.x -= speed
        # 翼龙动画
        if self.kind == 'ptero':
            self.frame_counter += 1
            if self.frame_counter >= 10:
                self.frame_counter = 0
                self.frame += 1

    def get_hitbox(self):
        """获取碰撞箱"""
        return get_hitbox(self.sprite, int(self.x), self.y)


class Cloud:
    """装饰性云朵"""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = y

    def update(self, speed):
        self.x -= speed * 0.3  # 云朵移动较慢 (视差效果)


class Star:
    """夜空星星"""

    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char


# ══════════════════════════════════════════════════════════════
# 主游戏类
# ══════════════════════════════════════════════════════════════

class Game:
    """恐龙跑酷游戏"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.ground_y = self.height - 3
        self.high_score = 0
        self.setup_colors()
        self.reset()

    def setup_colors(self):
        """初始化颜色"""
        curses.start_color()
        curses.use_default_colors()
        # 颜色对定义
        curses.init_pair(1, curses.COLOR_WHITE, -1)     # 白色 (恐龙)
        curses.init_pair(2, curses.COLOR_CYAN, -1)      # 青色 (分数)
        curses.init_pair(3, curses.COLOR_GREEN, -1)     # 绿色 (仙人掌)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)    # 黄色 (翼龙)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)  # 地面线
        curses.init_pair(6, curses.COLOR_BLUE, -1)      # 蓝色 (云)
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)   # 品红 (特效)
        curses.init_pair(8, curses.COLOR_RED, -1)       # 红色 (死亡)
        # 夜间颜色
        curses.init_pair(9, 8, -1)                      # 暗灰 (夜间恐龙)
        curses.init_pair(10, 2, -1)                     # 暗绿 (夜间仙人掌)
        curses.init_pair(11, 3, -1)                     # 暗黄 (夜间翼龙)

    def reset(self):
        """重置游戏状态"""
        self.player = Player(self.ground_y)
        self.obstacles = []
        self.clouds = []
        self.stars = []
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.night_mode = False
        self.night_transition = 0.0  # 0=白天, 1=夜晚
        self.distance = 0.0
        self.ground_offset = 0.0
        self.last_obstacle_x = self.width + 20
        self.frame_count = 0
        self.flash_timer = 0  # 100分闪烁

        # 初始化云朵
        for _ in range(3):
            x = random.randint(10, self.width - 10)
            y = random.randint(1, self.ground_y - 8)
            self.clouds.append(Cloud(x, y))

        # 初始化星星
        self._generate_stars()

    def _generate_stars(self):
        """生成星星"""
        self.stars = []
        for _ in range(15):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.ground_y - 6)
            char = random.choice(STARS)
            self.stars.append(Star(x, y, char))

    def spawn_obstacle(self):
        """生成新障碍物"""
        if self.last_obstacle_x > self.width - MIN_OBSTACLE_GAP:
            return

        # 根据分数决定障碍物类型
        roll = random.random()
        if self.score > 300 and roll < 0.2:
            kind = 'ptero'
        elif roll < 0.4:
            kind = 'double'
        elif roll < 0.7:
            kind = 'large'
        else:
            kind = 'small'

        x = self.width + random.randint(5, 20)
        obs = Obstacle(x, self.ground_y, kind, self.speed)
        self.obstacles.append(obs)
        self.last_obstacle_x = x

    def update(self):
        """更新游戏状态"""
        if self.game_over:
            return

        self.frame_count += 1

        # 更新速度
        self.speed = min(self.speed + SPEED_INCREMENT, MAX_SPEED)

        # 更新分数
        self.distance += self.speed * 0.1
        new_score = int(self.distance)
        # 每100分闪烁
        if new_score // 100 > self.score // 100:
            self.flash_timer = 15
        self.score = new_score

        # 日夜切换
        self.night_mode = (self.score // NIGHT_CYCLE) % 2 == 1
        target = 1.0 if self.night_mode else 0.0
        self.night_transition += (target - self.night_transition) * 0.02

        # 更新玩家
        self.player.update()

        # 更新障碍物
        for obs in self.obstacles:
            obs.update(self.speed)
        self.obstacles = [o for o in self.obstacles if o.x > -20]

        # 记录最右障碍物位置
        if self.obstacles:
            self.last_obstacle_x = max(o.x for o in self.obstacles)
        else:
            self.last_obstacle_x = 0

        # 生成障碍物
        gap = max(MIN_OBSTACLE_GAP, int(40 - self.speed))
        if self.last_obstacle_x < self.width - gap:
            if random.random() < 0.03 + self.speed * 0.005:
                self.spawn_obstacle()

        # 更新云朵
        for cloud in self.clouds:
            cloud.update(self.speed)
        self.clouds = [c for c in self.clouds if c.x > -10]
        if len(self.clouds) < 4 and random.random() < 0.01:
            y = random.randint(1, self.ground_y - 8)
            self.clouds.append(Cloud(self.width + 5, y))

        # 更新地面偏移
        self.ground_offset = (self.ground_offset + self.speed * 0.5) % 4

        # 闪烁计时器
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # 碰撞检测
        player_box = self.player.get_hitbox()
        for obs in self.obstacles:
            obs_box = obs.get_hitbox()
            if boxes_overlap(player_box, obs_box):
                self.die()
                return

    def die(self):
        """死亡处理"""
        self.game_over = True
        self.high_score = max(self.high_score, self.score)

    def handle_input(self):
        """处理输入"""
        key = self.stdscr.getch()
        if key == -1:
            return

        if self.game_over:
            if key in (ord('q'), ord('Q'), 27):  # Q / ESC
                return False  # 退出
            else:
                self.reset()
                return True

        if key in (ord(' '), curses.KEY_UP, ord('w'), ord('W')):
            self.player.jump()
        elif key == curses.KEY_DOWN or key in (ord('s'), ord('S')):
            self.player.duck(True)
        elif key in (ord('q'), ord('Q'), 27):
            return False

        return True

    def draw_sprite(self, sprite, x, y, color_pair=1):
        """在指定位置绘制精灵"""
        try:
            for dy, row in enumerate(sprite):
                if y + dy < 0 or y + dy >= self.height:
                    continue
                for dx, ch in enumerate(row):
                    if ch == ' ':
                        continue
                    sx, sy = x + dx, y + dy
                    if 0 <= sx < self.width - 1 and 0 <= sy < self.height - 1:
                        self.stdscr.addch(sy, sx, ch, curses.color_pair(color_pair))
        except curses.error:
            pass

    def draw_text(self, text, x, y, color_pair=1, bold=False):
        """安全绘制文本"""
        try:
            attr = curses.color_pair(color_pair)
            if bold:
                attr |= curses.A_BOLD
            if y < 0 or y >= self.height - 1:
                return
            if x < 0:
                text = text[-x:]
                x = 0
            if x + len(text) >= self.width:
                text = text[:self.width - x - 1]
            if text:
                self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def render(self):
        """渲染游戏画面"""
        self.stdscr.clear()

        # 根据日夜选择颜色方案
        nt = self.night_transition
        dino_color = 1 if nt < 0.5 else 9
        cactus_color = 3 if nt < 0.5 else 10
        ptero_color = 4 if nt < 0.5 else 11
        score_color = 2 if nt < 0.5 else 7

        # 绘制星星 (夜间)
        if nt > 0.3:
            for star in self.stars:
                if star.x < self.width - 1 and star.y < self.height - 1:
                    try:
                        self.stdscr.addch(star.y, star.x, star.char,
                                          curses.color_pair(7) | curses.A_DIM)
                    except curses.error:
                        pass

        # 绘制云朵
        for cloud in self.clouds:
            self.draw_sprite(CLOUD, int(cloud.x), cloud.y, 6)

        # 绘制地面
        ground_line = ""
        for i in range(self.width):
            idx = int(i + self.ground_offset) % len(GROUND_CHARS)
            ground_line += GROUND_CHARS[idx]
        self.draw_text(ground_line, 0, self.ground_y, 5)

        # 地面下方点缀
        for i in range(0, self.width, 7):
            offset = int(i + self.ground_offset * 2) % 13
            if offset < 3:
                x = i + offset
                if x < self.width - 1:
                    try:
                        self.stdscr.addch(self.ground_y + 1, x, '▁',
                                          curses.color_pair(dino_color) | curses.A_DIM)
                    except curses.error:
                        pass

        # 绘制障碍物
        for obs in self.obstacles:
            color = ptero_color if obs.kind == 'ptero' else cactus_color
            self.draw_sprite(obs.sprite, int(obs.x), obs.y, color)

        # 绘制玩家
        if self.game_over:
            self.draw_sprite(DINO_DEAD, self.player.x, self.player.screen_y, 8)
        else:
            self.draw_sprite(self.player.sprite, self.player.x, self.player.screen_y, dino_color)

        # 绘制分数
        if self.flash_timer > 0 and self.flash_timer % 4 < 2:
            score_text = f"HI {self.high_score:05d}    {self.score:05d}"
        else:
            score_text = f"HI {self.high_score:05d}    {self.score:05d}"
        self.draw_text(score_text, self.width - len(score_text) - 2, 1, score_color, bold=True)

        # 速度指示器
        speed_text = f"SPD {self.speed:.1f}"
        self.draw_text(speed_text, 2, 1, score_color)

        # 游戏结束画面
        if self.game_over:
            # 半透明效果 — 通过清空中间区域模拟
            center_y = self.height // 2
            center_x = self.width // 2

            # 游戏结束文字
            game_over_text = "░▒▓ GAME OVER ▓▒░"
            self.draw_text(game_over_text,
                          center_x - len(game_over_text) // 2, center_y - 3, 8, bold=True)

            # 分数
            score_str = f"Score: {self.score}"
            self.draw_text(score_str,
                          center_x - len(score_str) // 2, center_y - 1, 2, bold=True)

            hi_str = f"Best:  {self.high_score}"
            self.draw_text(hi_str,
                          center_x - len(hi_str) // 2, center_y, 7, bold=True)

            # 提示
            restart_text = "Press any key to restart"
            self.draw_text(restart_text,
                          center_x - len(restart_text) // 2, center_y + 2, 1)

            quit_text = "Press Q or ESC to quit"
            self.draw_text(quit_text,
                          center_x - len(quit_text) // 2, center_y + 3, 1)

        # 等待开始画面
        elif self.score == 0 and self.distance == 0 and self.frame_count < 30:
            center_y = self.height // 2
            center_x = self.width // 2
            title = "🦕 DINO RUN"
            self.draw_text(title, center_x - len(title) // 2, center_y - 2, 2, bold=True)
            sub = "The classic T-Rex game in your terminal"
            self.draw_text(sub, center_x - len(sub) // 2, center_y, 1)
            hint = "Press SPACE to start!"
            self.draw_text(hint, center_x - len(hint) // 2, center_y + 2, 7, bold=True)

        self.stdscr.refresh()

    def run(self):
        """主游戏循环"""
        curses.curs_set(0)       # 隐藏光标
        self.stdscr.nodelay(True) # 非阻塞输入
        self.stdscr.timeout(int(FRAME_TIME * 1000))

        running = True
        while running:
            # 处理输入
            result = self.handle_input()
            if result is False:
                break
            if result is None:
                running = False
                break

            # 如果还没开始，不更新物理
            if self.score == 0 and self.distance == 0:
                # 检查是否按了跳跃键来开始
                pass

            self.update()
            self.render()

        return self.high_score


# ══════════════════════════════════════════════════════════════
# 终端大小检查
# ══════════════════════════════════════════════════════════════

def check_terminal_size():
    """检查终端大小是否足够"""
    try:
        size = os.get_terminal_size()
        if size.lines < 16 or size.columns < 50:
            print(f"⚠️  Terminal too small! Need at least 50×16, got {size.columns}×{size.lines}")
            print("   Please resize your terminal and try again.")
            return False
    except OSError:
        pass
    return True


# ══════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════

def main():
    """启动游戏"""
    if not check_terminal_size():
        sys.exit(1)

    print("🦕 dino — Starting game...")
    print("   Controls: SPACE/UP=Jump  DOWN=Duck  Q=Quit")

    try:
        high_score = curses.wrapper(lambda s: Game(s).run())
    except KeyboardInterrupt:
        print("\n🦕 Thanks for playing!")
        return

    print(f"\n🦕 Game Over! Best score: {high_score}")


if __name__ == "__main__":
    main()
