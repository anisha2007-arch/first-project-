import tkinter as tk
import random
import time

GRID_COUNT = 20
INITIAL_W = 520
INITIAL_H = 580
BASE_SPEED = 150
MIN_SPEED = 55
MAX_LIVES = 3

THEMES = [
    {
        "name": "Matrix",
        "bg": "#111111", "head": "#4CAF50", "body": "#81C784",
        "food": "#FF5722", "golden": "#FFD700", "slow": "#7B68EE",
        "shrink": "#FF69B4", "text": "#FFFFFF", "hint": "#333333",
        "hud_bg": "#111111", "hud_fg": "#AAAAAA",
    },
    {
        "name": "Ocean",
        "bg": "#0D1B2A", "head": "#00E5FF", "body": "#00838F",
        "food": "#FF6D00", "golden": "#FFD700", "slow": "#CE93D8",
        "shrink": "#F48FB1", "text": "#E0F7FA", "hint": "#1A3A5C",
        "hud_bg": "#0D1B2A", "hud_fg": "#80CBC4",
    },
    {
        "name": "Neon",
        "bg": "#0A0A0A", "head": "#FF00FF", "body": "#8B008B",
        "food": "#00FF41", "golden": "#FFD700", "slow": "#00BFFF",
        "shrink": "#FF69B4", "text": "#FFFFFF", "hint": "#222222",
        "hud_bg": "#0A0A0A", "hud_fg": "#FF00FF",
    },
]

class SnakeGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Snake Deluxe")
        self.window.geometry(f"{INITIAL_W}x{INITIAL_H}")
        self.window.minsize(320, 380)

        self.theme_idx = 0
        self.high_score = 0
        self._loop_id = None

        self._build_hud()

        self.canvas = tk.Canvas(window, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.window.bind("<Key>", self.handle_keypress)
        self.window.bind("<space>", self.handle_space)
        self.window.bind("p", self.toggle_pause)
        self.window.bind("P", self.toggle_pause)
        self.window.bind("w", self.toggle_wrap)
        self.window.bind("W", self.toggle_wrap)
        self.window.bind("t", self.toggle_theme)
        self.window.bind("T", self.toggle_theme)

        self.lives = MAX_LIVES
        self.score = 0
        self.wrap_mode = False
        self.reset_round()
        self.game_loop()

    def _build_hud(self):
        t = THEMES[self.theme_idx]
        self.hud = tk.Frame(self.window, bg=t["hud_bg"], height=54)
        self.hud.pack(fill=tk.X, side=tk.TOP)
        self.hud.pack_propagate(False)

        font_bold = ("Courier", 12, "bold")
        font_sm = ("Courier", 9)

        self.score_lbl = tk.Label(self.hud, text="Score: 0", fg=t["head"], bg=t["hud_bg"], font=font_bold)
        self.score_lbl.pack(side=tk.LEFT, padx=12, pady=4)

        self.hi_lbl = tk.Label(self.hud, text="Best: 0", fg="#FFD700", bg=t["hud_bg"], font=font_bold)
        self.hi_lbl.pack(side=tk.LEFT, padx=4)

        self.lives_lbl = tk.Label(self.hud, text="♥ ♥ ♥", fg="#FF4444", bg=t["hud_bg"], font=font_bold)
        self.lives_lbl.pack(side=tk.RIGHT, padx=12, pady=4)

        self.status_lbl = tk.Label(self.hud, text="", fg=t["hud_fg"], bg=t["hud_bg"], font=font_sm)
        self.status_lbl.pack(side=tk.RIGHT, padx=8)

        self.theme_lbl = tk.Label(self.hud, text=f"[{t['name']}]", fg=t["hud_fg"], bg=t["hud_bg"], font=font_sm)
        self.theme_lbl.pack(side=tk.RIGHT, padx=4)

    def _refresh_hud_colors(self):
        t = THEMES[self.theme_idx]
        self.hud.config(bg=t["hud_bg"])
        self.score_lbl.config(fg=t["head"], bg=t["hud_bg"])
        self.hi_lbl.config(bg=t["hud_bg"])
        self.status_lbl.config(fg=t["hud_fg"], bg=t["hud_bg"])
        self.theme_lbl.config(fg=t["hud_fg"], bg=t["hud_bg"], text=f"[{t['name']}]")
        self.lives_lbl.config(bg=t["hud_bg"])
        self.canvas.config(bg=t["bg"])

    def update_hud(self):
        t = THEMES[self.theme_idx]
        self.score_lbl.config(text=f"Score: {self.score}")
        self.hi_lbl.config(text=f"Best: {self.high_score}")
        hearts = ("♥ " * self.lives + "♡ " * (MAX_LIVES - self.lives)).strip()
        self.lives_lbl.config(text=hearts)
        parts = []
        if self.wrap_mode:
            parts.append("WRAP")
        if time.time() < self.slow_until:
            parts.append("SLOW")
        self.status_lbl.config(text="  ".join(parts), fg=t["hud_fg"])

    def reset_round(self):
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = None
        self.special_food = None      
        self.game_over = False
        self.paused = False
        self.slow_until = 0
        self.flash_until = 0
        self.spawn_food()
        self.update_hud()

    def get_speed(self):
        spd = max(MIN_SPEED, BASE_SPEED - self.score * 3)
        if time.time() < self.slow_until:
            spd = int(spd * 1.9)
        return spd

    def _occupied(self):
        occ = set(self.snake)
        if self.food:
            occ.add(self.food)
        if self.special_food:
            occ.add((self.special_food[0], self.special_food[1]))
        return occ

    def spawn_food(self):
        occ = self._occupied()
        while True:
            pos = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if pos not in occ:
                self.food = pos
                break
        if not self.special_food and random.random() < 0.35:
            self.spawn_special()

    def spawn_special(self):
        occ = self._occupied()
        for _ in range(60):
            pos = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if pos not in occ:
                kind = random.choices(
                    ["golden", "slow", "shrink"],
                    weights=[0.4, 0.35, 0.25]
                )[0]
                self.special_food = (pos[0], pos[1], kind, time.time() + 7)
                return

    def handle_keypress(self, event):
        if self.game_over or self.paused:
            return
        opposites = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
        k = event.keysym
        if k in opposites and k != opposites.get(self.direction):
            self.next_direction = k

    def handle_space(self, event=None):
        if self.game_over:
            self.lives = MAX_LIVES
            self.score = 0
            self.reset_round()
            self.game_loop()
        else:
            self.toggle_pause()

    def toggle_pause(self, event=None):
        if self.game_over:
            return
        self.paused = not self.paused
        if not self.paused:
            self.game_loop()
        else:
            self.draw_elements()

    def toggle_wrap(self, event=None):
        self.wrap_mode = not self.wrap_mode
        self.update_hud()

    def toggle_theme(self, event=None):
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        self._refresh_hud_colors()
        self.update_hud()

    def move_snake(self):
        self.direction = self.next_direction
        hx, hy = self.snake[0]
        dx, dy = {"Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0)}[self.direction]
        nx, ny = hx + dx, hy + dy

        if self.wrap_mode:
            nx %= GRID_COUNT
            ny %= GRID_COUNT
        elif not (0 <= nx < GRID_COUNT and 0 <= ny < GRID_COUNT):
            self._die()
            return

        new_head = (nx, ny)
        if new_head in self.snake:
            self._die()
            return

        self.snake.insert(0, new_head)
        grow = False

        if new_head == self.food:
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self.flash_until = time.time() + 0.1
            self.spawn_food()
            grow = True

        if self.special_food and new_head == (self.special_food[0], self.special_food[1]):
            kind = self.special_food[2]
            self.special_food = None
            self.flash_until = time.time() + 0.18
            if kind == "golden":
                self.score += 3
                if self.score > self.high_score:
                    self.high_score = self.score
                grow = True
            elif kind == "slow":
                self.slow_until = time.time() + 5
                self.score += 1
            elif kind == "shrink":
                self.score += 1
                trim = min(2, len(self.snake) - 3)
                for _ in range(trim):
                    self.snake.pop()

        if not grow:
            self.snake.pop()

        if self.special_food and time.time() > self.special_food[3]:
            self.special_food = None

        self.update_hud()

    def _die(self):
        self.lives -= 1
        self.update_hud()
        if self.lives <= 0:
            self.game_over = True
        else:
            self.snake = [(5, 10), (4, 10), (3, 10)]
            self.direction = "Right"
            self.next_direction = "Right"
            self.special_food = None
            self.slow_until = 0

    def draw_elements(self):
        t = THEMES[self.theme_idx]
        c = self.canvas
        c.delete("all")

        cw = c.winfo_width() or INITIAL_W
        ch = c.winfo_height() or (INITIAL_H - 54)
        board = min(cw, ch) - 4
        gs = board / GRID_COUNT
        xo = (cw - board) / 2
        yo = (ch - board) / 2

        c.create_rectangle(xo-1, yo-1, xo+board+1, yo+board+1, outline=t["head"], width=1)

        if self.game_over:
            c.create_text(cw/2, ch/2 - 50, text="GAME OVER", fill="#FF3333", font=("Courier", 32, "bold"))
            c.create_text(cw/2, ch/2 + 2, text=f"Score: {self.score}", fill=t["text"], font=("Courier", 16, "bold"))
            c.create_text(cw/2, ch/2 + 32, text=f"Best: {self.high_score}", fill="#FFD700", font=("Courier", 14))
            c.create_text(cw/2, ch/2 + 62, text="SPACE — play again", fill="#666666", font=("Courier", 11))
            return

        if self.paused:
            c.create_text(cw/2, ch/2 - 20, text="⏸  PAUSED", fill=t["text"], font=("Courier", 26, "bold"))
            c.create_text(cw/2, ch/2 + 20, text="P or SPACE to resume", fill="#666666", font=("Courier", 11))
            return

        if time.time() < self.flash_until:
            c.create_rectangle(xo, yo, xo+board, yo+board, fill="white", stipple="gray25", outline="")

        fx, fy = self.food
        m = gs * 0.12
        c.create_oval(xo+fx*gs+m, yo+fy*gs+m, xo+(fx+1)*gs-m, yo+(fy+1)*gs-m, fill=t["food"], outline="")

        if self.special_food:
            sx, sy, skind, exp = self.special_food
            scolor = t.get(skind, "#FFFFFF")
            remaining = exp - time.time()
            if remaining > 2 or int(remaining * 4) % 2 == 0:
                cx_ = xo + sx*gs + gs/2
                cy_ = yo + sy*gs + gs/2
                r = gs * 0.46
                c.create_polygon(cx_, cy_-r, cx_+r*0.65, cy_, cx_, cy_+r, cx_-r*0.65, cy_, fill=scolor, outline="white", width=1)
                labels = {"golden": "+3", "slow": "zz", "shrink": "—2"}
                c.create_text(cx_, cy_, text=labels[skind], fill="black", font=("Courier", max(6, int(gs*0.35)), "bold"))

        for i, (sx, sy) in enumerate(self.snake):
            color = t["head"] if i == 0 else t["body"]
            pad = max(1, gs * 0.06)
            x0 = xo + sx*gs + pad
            y0 = yo + sy*gs + pad
            x1 = xo + (sx+1)*gs - pad
            y1 = yo + (sy+1)*gs - pad
            c.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

            if i == 0:
                er = max(1.5, gs * 0.1)
                off = gs * 0.22
                if self.direction == "Right": eyes = [(x1 - off, y0 + off*0.9), (x1 - off, y1 - off*0.9)]
                elif self.direction == "Left": eyes = [(x0 + off, y0 + off*0.9), (x0 + off, y1 - off*0.9)]
                elif self.direction == "Up": eyes = [(x0 + off*0.9, y0 + off), (x1 - off*0.9, y0 + off)]
                else: eyes = [(x0 + off*0.9, y1 - off), (x1 - off*0.9, y1 - off)]
                for ex, ey in eyes:
                    c.create_oval(ex-er, ey-er, ex+er, ey+er, fill="white", outline="")
                    c.create_oval(ex-er*0.5, ey-er*0.5, ex+er*0.5, ey+er*0.5, fill="#111111", outline="")

        hints = "Arrows:Move  P:Pause  W:Wrap  T:Theme  Space:Pause/Restart"
        c.create_text(cw/2, yo+board+10, text=hints, fill=t["hint"], font=("Courier", 7))

    def game_loop(self):
        if self._loop_id:
            self.window.after_cancel(self._loop_id)
            self._loop_id = None
        if self.paused or self.game_over:
            self.draw_elements()
            return
        self.move_snake()
        self.draw_elements()
        self._loop_id = self.window.after(self.get_speed(), self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()