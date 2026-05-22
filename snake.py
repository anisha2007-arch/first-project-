import tkinter as tk
import random

# --- INITIAL CONFIGURATION ---
GRID_COUNT = 20
INITIAL_WINDOW_SIZE = 400
GAME_SPEED = 150  

class SnakeGame:
    def __init__(self, window):
        self.window = window
        self.window.title("Responsive Square Snake")
        self.window.geometry(f"{INITIAL_WINDOW_SIZE}x{INITIAL_WINDOW_SIZE}")
        
        # FIXED: Added 'expand=True' and 'fill=tk.BOTH' so the canvas grows when you maximize
        self.canvas = tk.Canvas(window, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind controls
        self.window.bind("<Key>", self.handle_keypress)
        self.window.bind("<space>", self.restart_game)
        
        self.reset_game_state()
        self.game_loop()

    def reset_game_state(self):
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = "Right"
        self.food = None
        self.game_over = False
        self.spawn_food()

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_COUNT - 1)
            y = random.randint(0, GRID_COUNT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def handle_keypress(self, event):
        if self.game_over:
            return
        new_dir = event.keysym
        all_dirs = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
        if new_dir in all_dirs and new_dir != all_dirs.get(self.direction):
            self.direction = new_dir

    def restart_game(self, event):
        if self.game_over:
            self.reset_game_state()
            self.game_loop()

    def move_snake(self):
        head_x, head_y = self.snake[0]
        
        if self.direction == "Up": head_y -= 1
        elif self.direction == "Down": head_y += 1
        elif self.direction == "Left": head_x -= 1
        elif self.direction == "Right": head_x += 1
        
        new_head = (head_x, head_y)
        
        if (head_x < 0 or head_x >= GRID_COUNT or 
            head_y < 0 or head_y >= GRID_COUNT or 
            new_head in self.snake):
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            self.spawn_food()
        else:
            self.snake.pop()

    def draw_elements(self):
        self.canvas.delete("all")
        
        # DYNAMIC SCALING: Read the canvas dimensions in real-time
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Pick the smaller dimension to keep the game board perfectly square
        board_size = min(canvas_width, canvas_height)
        grid_size = board_size / GRID_COUNT
        
        # Center the game board inside the window frame
        x_offset = (canvas_width - board_size) / 2
        y_offset = (canvas_height - board_size) / 2
        
        if self.game_over:
            self.canvas.create_text(canvas_width/2, canvas_height/2 - 20, 
                                    text="GAME OVER", fill="#FF3333", font=("Arial", 24, "bold"))
            self.canvas.create_text(canvas_width/2, canvas_height/2 + 20, 
                                    text="Press SPACEBAR to Play Again", fill="#FFFFFF", font=("Arial", 12))
            return
            
        # Draw Food using the calculated dynamic grid layout
        fx, fy = self.food
        self.canvas.create_rectangle(x_offset + fx*grid_size, y_offset + fy*grid_size, 
                                     x_offset + (fx+1)*grid_size, y_offset + (fy+1)*grid_size, 
                                     fill="#FF5722", outline="")
        
        # Draw Snake Segments using the calculated dynamic grid layout
        for i, (sx, sy) in enumerate(self.snake):
            color = "#4CAF50" if i == 0 else "#81C784"
            self.canvas.create_rectangle(x_offset + sx*grid_size, y_offset + sy*grid_size, 
                                         x_offset + (sx+1)*grid_size, y_offset + (sy+1)*grid_size, 
                                         fill=color, outline="#111111")

    def game_loop(self):
        if not self.game_over:
            self.move_snake()
            self.draw_elements()
            self.window.after(GAME_SPEED, self.game_loop)
        else:
            self.draw_elements()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()