import tkinter as tk
import random
import time

# --- CONSTANTS FOR THE WINDOW LAYOUT ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
CANVAS_HEIGHT = 400

# --- VISUALIZATION LOGIC ---

def draw_bars(data, canvas, color_list):
    """Clears the canvas and redraws the array as vertical bars."""
    canvas.delete("all")
    
    # Calculate dynamic width for bars based on how many elements are in the data array
    bar_width = WINDOW_WIDTH / len(data)
    # Normalize data so the tallest bar fits perfectly within the canvas height
    max_value = max(data) if data else 1
    
    for i, value in enumerate(data):
        # Coordinates for each bar (top-left and bottom-right corners)
        x0 = i * bar_width
        y0 = CANVAS_HEIGHT - (value / max_value * (CANVAS_HEIGHT - 20))
        x1 = (i + 1) * bar_width
        y1 = CANVAS_HEIGHT
        
        # Draw the rectangle bar
        canvas.create_rectangle(x0, y0, x1, y1, fill=color_list[i], outline="white")

def generate_array(data, canvas, size_slider):
    """Generates a new random array based on the slider value and draws it."""
    global array_data
    array_size = size_slider.get()
    
    # Generate random numbers between 10 and 100
    array_data = [random.randint(10, 100) for _ in range(array_size)]
    
    # Initial color for all bars is teal/blue-green
    default_colors = ["#4A90E2"] * array_size
    draw_bars(array_data, canvas, default_colors)

def bubble_sort(data, canvas, window, speed_slider):
    """Manually executes Bubble Sort, updating the canvas on every swap."""
    n = len(data)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            # Highlight the two bars currently being compared in Orange
            colors = ["#4A90E2"] * n
            colors[j] = "#F5A623"
            colors[j + 1] = "#F5A623"
            draw_bars(data, canvas, colors)
            window.update()
            time.sleep(speed_slider.get())
            
            # If they are out of order, swap them
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                
                # Highlight the swapped bars in Red to show action
                colors[j] = "#E15759"
                colors[j + 1] = "#E15759"
                draw_bars(data, canvas, colors)
                window.update()
                time.sleep(speed_slider.get())
                
        # Mark the elements at the end of the array as completely sorted using Green
        colors = ["#4A90E2"] * n
        for k in range(n - i - 1, n):
            colors[k] = "#2CA02C"
    
    # Final draw to turn the entire completed array Green
    draw_bars(data, canvas, ["#2CA02C"] * n)

# --- GUI INITIALIZATION ---

# Create main application window
root = tk.Tk()
root.title("DSA Sorting Algorithm Visualizer")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.config(bg="#F0F2F5")

# Global data variable to hold current array
array_data = []

# Top Frame: Control Panel for Buttons and Sliders
control_frame = tk.Frame(root, width=WINDOW_WIDTH, height=100, bg="#FFFFFF", relief=tk.RIDGE, bd=1)
control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Bottom Canvas: Where the bars are drawn
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=CANVAS_HEIGHT, bg="#FFFFFF", highlightthickness=0)
canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

# Control Elements: Sliders for Array Size and Speed
size_label = tk.Label(control_frame, text="Array Size:", bg="#FFFFFF", font=("Arial", 10, "bold"))
size_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

size_slider = tk.Scale(control_frame, from_=10, to=100, orient=tk.HORIZONTAL, bg="#FFFFFF", highlightthickness=0)
size_slider.set(30) # Default size
size_slider.grid(row=0, column=1, padx=5, pady=5)

speed_label = tk.Label(control_frame, text="Delay (sec):", bg="#FFFFFF", font=("Arial", 10, "bold"))
speed_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

# Slider to control how long the animation pauses between swaps
speed_slider = tk.Scale(control_frame, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, bg="#FFFFFF", highlightthickness=0)
speed_slider.set(0.05) # Default speed
speed_slider.grid(row=0, column=3, padx=5, pady=5)

# Control Buttons
# FIXED: Changed 'bdc=0' to 'bd=0' to eliminate the TclError
generate_btn = tk.Button(control_frame, text="Generate Array", font=("Arial", 10, "bold"), bg="#4A90E2", fg="white", 
                         activebackground="#357ABD", activeforeground="white", bd=0, relief=tk.FLAT,
                         command=lambda: generate_array(array_data, canvas, size_slider))
generate_btn.grid(row=0, column=4, padx=15, pady=5)

sort_btn = tk.Button(control_frame, text="Start Bubble Sort", font=("Arial", 10, "bold"), bg="#2CA02C", fg="white",
                     activebackground="#217A21", activeforeground="white", bd=0, relief=tk.FLAT,
                     command=lambda: bubble_sort(array_data, canvas, root, speed_slider))
sort_btn.grid(row=0, column=5, padx=15, pady=5)

# Generate an initial array automatically on startup
generate_array(array_data, canvas, size_slider)

# Run the Tkinter main event loop
root.mainloop()