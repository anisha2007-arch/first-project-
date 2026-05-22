import tkinter as tk
from tkinter import ttk
import random
import time

BG        = "#1E1E2E"
CANVAS_BG = "#13131F"
BAR_DEF   = "#4A90E2"
BAR_CMP   = "#F5A623"   
BAR_SWAP  = "#E15759"   
BAR_DONE  = "#2ECC71"   
BAR_PIVOT = "#9B59B6"   
BAR_SEL   = "#E74C3C"   
TEXT_FG   = "#CDD6F4"
ACCENT    = "#89B4FA"
PANEL_BG  = "#181825"

ALGO_INFO = {
    "Bubble Sort":    "O(n²)  — Repeatedly swaps adjacent out-of-order pairs. Simple, slow.",
    "Insertion Sort": "O(n²) avg — Grows a sorted prefix one element at a time. Fast on nearly-sorted data.",
    "Selection Sort": "O(n²)  — Finds minimum each pass, places it. Minimum swaps.",
    "Merge Sort":      "O(n log n) — Divides in half recursively, merges sorted halves. Stable.",
    "Quick Sort":      "O(n log n) avg — Partitions around a pivot recursively. In-place.",
    "Heap Sort":       "O(n log n) — Builds max-heap, extracts max repeatedly. In-place.",
}

def bubble_sort_gen(data):
    n = len(data)
    comps = swaps = 0
    sorted_from = n
    for i in range(n):
        for j in range(n - i - 1):
            colors = [BAR_DEF] * n
            for k in range(sorted_from - 1, n): colors[k] = BAR_DONE
            colors[j] = BAR_CMP
            colors[j+1] = BAR_CMP
            comps += 1
            yield data[:], colors, comps, swaps
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
                swaps += 1
                colors[j] = BAR_SWAP
                colors[j+1] = BAR_SWAP
                yield data[:], colors, comps, swaps
        sorted_from -= 1
    yield data[:], [BAR_DONE] * n, comps, swaps

def insertion_sort_gen(data):
    n = len(data)
    comps = swaps = 0
    for i in range(1, n):
        key = data[i]
        j = i - 1
        colors = [BAR_DEF] * n
        colors[i] = BAR_SEL
        yield data[:], colors, comps, swaps
        while j >= 0:
            comps += 1
            colors = [BAR_DEF] * n
            colors[i] = BAR_SEL
            colors[j] = BAR_CMP
            yield data[:], colors, comps, swaps
            if data[j] > key:
                data[j+1] = data[j]
                swaps += 1
                colors[j] = BAR_SWAP
                colors[j+1] = BAR_SWAP
                j -= 1
                yield data[:], colors, comps, swaps
            else:
                break
        data[j+1] = key
    yield data[:], [BAR_DONE] * n, comps, swaps

def selection_sort_gen(data):
    n = len(data)
    comps = swaps = 0
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            comps += 1
            colors = [BAR_DEF] * n
            for k in range(i): colors[k] = BAR_DONE
            colors[min_idx] = BAR_SEL
            colors[j] = BAR_CMP
            yield data[:], colors, comps, swaps
            if data[j] < data[min_idx]: min_idx = j
        if min_idx != i:
            data[i], data[min_idx] = data[min_idx], data[i]
            swaps += 1
            colors = [BAR_DEF] * n
            for k in range(i): colors[k] = BAR_DONE
            colors[i] = BAR_SWAP
            colors[min_idx] = BAR_SWAP
            yield data[:], colors, comps, swaps
    yield data[:], [BAR_DONE] * n, comps, swaps

def merge_sort_gen(data):
    comps, swaps = [0], [0]
    def merge(arr, l, m, r):
        left, right = arr[l:m+1], arr[m+1:r+1]
        i = j = 0
        k = l
        while i < len(left) and j < len(right):
            comps[0] += 1
            c = [BAR_DEF] * len(arr)
            for x in range(l, r+1): c[x] = BAR_CMP
            yield arr[:], c, comps[0], swaps[0]
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
                swaps[0] += 1
            c2 = [BAR_DEF] * len(arr)
            c2[k] = BAR_SWAP
            yield arr[:], c2, comps[0], swaps[0]
            k += 1
        while i < len(left):
            arr[k] = left[i]; i += 1; k += 1
        while j < len(right):
            arr[k] = right[j]; j += 1; k += 1

    def merge_sort(arr, l, r):
        if l < r:
            m = (l + r) // 2
            yield from merge_sort(arr, l, m)
            yield from merge_sort(arr, m+1, r)
            yield from merge(arr, l, m, r)

    yield from merge_sort(data, 0, len(data)-1)
    yield data[:], [BAR_DONE] * len(data), comps[0], swaps[0]

def quick_sort_gen(data):
    comps, swaps = [0], [0]
    stack = [(0, len(data)-1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi: continue
        pivot_val = data[hi]
        i = lo - 1
        for j in range(lo, hi):
            comps[0] += 1
            c = [BAR_DEF] * len(data)
            c[hi] = BAR_PIVOT
            c[j] = BAR_CMP
            yield data[:], c, comps[0], swaps[0]
            if data[j] <= pivot_val:
                i += 1
                if i != j:
                    data[i], data[j] = data[j], data[i]
                    swaps[0] += 1
                    c2 = [BAR_DEF] * len(data)
                    c2[hi] = BAR_PIVOT; c2[i] = BAR_SWAP; c2[j] = BAR_SWAP
                    yield data[:], c2, comps[0], swaps[0]
        data[i+1], data[hi] = data[hi], data[i+1]
        swaps[0] += 1
        pi = i + 1
        stack.append((lo, pi - 1))
        stack.append((pi + 1, hi))
    yield data[:], [BAR_DONE] * len(data), comps[0], swaps[0]

def heap_sort_gen(data):
    n = len(data)
    comps, swaps = [0], [0]
    def heapify(arr, size, root):
        largest = root
        l, r = 2 * root + 1, 2 * root + 2
        if l < size:
            comps[0] += 1
            c = [BAR_DEF] * n; c[root] = BAR_SEL; c[l] = BAR_CMP
            yield arr[:], c, comps[0], swaps[0]
            if arr[l] > arr[largest]: largest = l
        if r < size:
            comps[0] += 1
            c = [BAR_DEF] * n; c[largest] = BAR_SEL; c[r] = BAR_CMP
            yield arr[:], c, comps[0], swaps[0]
            if arr[r] > arr[largest]: largest = r
        if largest != root:
            arr[root], arr[largest] = arr[largest], arr[root]
            swaps[0] += 1
            c = [BAR_DEF] * n; c[root] = BAR_SWAP; c[largest] = BAR_SWAP
            yield arr[:], c, comps[0], swaps[0]
            yield from heapify(arr, size, largest)

    for i in range(n // 2 - 1, -1, -1): yield from heapify(data, n, i)
    for i in range(n - 1, 0, -1):
        data[0], data[i] = data[i], data[0]
        swaps[0] += 1
        c = [BAR_DEF] * n; c[0] = BAR_SWAP; c[i] = BAR_SWAP
        for k in range(i, n): c[k] = BAR_DONE
        yield data[:], c, comps[0], swaps[0]
        yield from heapify(data, i, 0)
    yield data[:], [BAR_DONE] * n, comps[0], swaps[0]

ALGO_GENS = {"Bubble Sort": bubble_sort_gen, "Insertion Sort": insertion_sort_gen, "Selection Sort": selection_sort_gen, "Merge Sort": merge_sort_gen, "Quick Sort": quick_sort_gen, "Heap Sort": heap_sort_gen}

def make_array(size, dist):
    if dist == "Random": return [random.randint(5, 100) for _ in range(size)]
    elif dist == "Sorted": return sorted([random.randint(5, 100) for _ in range(size)])
    elif dist == "Reversed": return sorted([random.randint(5, 100) for _ in range(size)], reverse=True)
    elif dist == "Few Unique":
        vals = [random.randint(10, 90) for _ in range(5)]
        return [random.choice(vals) for _ in range(size)]
    elif dist == "Mountain":
        half = [random.randint(5, 100) for _ in range(size // 2)]
        return sorted(half) + sorted(half, reverse=True)
    elif dist == "Valley":
        half = [random.randint(5, 100) for _ in range(size // 2)]
        return sorted(half, reverse=True) + sorted(half)
    return [random.randint(5, 100) for _ in range(size)]

class SortVisualiser:
    def __init__(self, root):
        self.root = root
        self.root.title("Sort Visualiser — Deluxe")
        self.root.configure(bg=BG)
        self.root.geometry("960x620")
        self.root.minsize(700, 480)
        self.array_data, self.generator = [], None
        self.running = self.paused = self.step_mode = False
        self._after_id = None
        self.comparisons = self.swaps = 0
        self.start_time = None
        self._build_ui()
        self.generate_array()

    def _build_ui(self):
        ctrl = tk.Frame(self.root, bg=PANEL_BG, pady=6)
        ctrl.pack(fill=tk.X)
        row1 = tk.Frame(ctrl, bg=PANEL_BG); row1.pack(fill=tk.X, padx=10, pady=2)
        self._lbl(row1, "Algorithm:").grid(row=0, column=0, padx=(0,4))
        self.algo_var = tk.StringVar(value="Bubble Sort")
        algo_menu = ttk.Combobox(row1, textvariable=self.algo_var, values=list(ALGO_GENS.keys()), state="readonly", width=15)
        algo_menu.grid(row=0, column=1, padx=(0,16))
        algo_menu.bind("<<ComboboxSelected>>", lambda e: self._on_algo_change())

        self._lbl(row1, "Distribution:").grid(row=0, column=2, padx=(0,4))
        self.dist_var = tk.StringVar(value="Random")
        ttk.Combobox(row1, textvariable=self.dist_var, values=["Random","Sorted","Reversed","Few Unique","Mountain","Valley"], state="readonly", width=12).grid(row=0, column=3, padx=(0,16))

        self._lbl(row1, "Size:").grid(row=0, column=4, padx=(0,4))
        self.size_var = tk.IntVar(value=40)
        tk.Scale(row1, variable=self.size_var, from_=10, to=120, orient=tk.HORIZONTAL, bg=PANEL_BG, fg=TEXT_FG, troughcolor="#2A2A40", highlightthickness=0, length=110).grid(row=0, column=5, padx=(0,16))

        self._lbl(row1, "Delay(ms):").grid(row=0, column=6, padx=(0,4))
        self.speed_var = tk.IntVar(value=30)
        tk.Scale(row1, variable=self.speed_var, from_=1, to=300, orient=tk.HORIZONTAL, bg=PANEL_BG, fg=TEXT_FG, troughcolor="#2A2A40", highlightthickness=0, length=110).grid(row=0, column=7, padx=(0,8))

        row2 = tk.Frame(ctrl, bg=PANEL_BG); row2.pack(fill=tk.X, padx=10, pady=4)
        btn_cfg = dict(font=("Courier", 10, "bold"), bd=0, relief=tk.FLAT, cursor="hand2", padx=10, pady=4)
        self.gen_btn = tk.Button(row2, text="⟳ Generate", bg=ACCENT, fg="#0D1B2A", command=self.generate_array, **btn_cfg); self.gen_btn.grid(row=0, column=0, padx=(0,6))
        self.sort_btn = tk.Button(row2, text="▶ Sort", bg="#2ECC71", fg="#0D1B2A", command=self.start_sort, **btn_cfg); self.sort_btn.grid(row=0, column=1, padx=(0,6))
        self.pause_btn = tk.Button(row2, text="⏸ Pause", bg="#F5A623", fg="#0D1B2A", command=self.toggle_pause, state=tk.DISABLED, **btn_cfg); self.pause_btn.grid(row=0, column=2, padx=(0,6))
        self.step_btn = tk.Button(row2, text="⏭ Step", bg="#9B59B6", fg="white", command=self.step_once, state=tk.DISABLED, **btn_cfg); self.step_btn.grid(row=0, column=3, padx=(0,6))
        tk.Button(row2, text="✕ Reset", bg="#E15759", fg="white", command=self.reset, **btn_cfg).grid(row=0, column=4, padx=(0,20))

        self.cmp_lbl = self._stat_lbl(row2, "Comparisons: 0", 5)
        self.swap_lbl = self._stat_lbl(row2, "Swaps: 0", 6)
        self.time_lbl = self._stat_lbl(row2, "Time: —", 7)

        self.info_bar = tk.Label(self.root, text=ALGO_INFO["Bubble Sort"], bg=PANEL_BG, fg="#888AAA", font=("Courier", 9), anchor=tk.W, padx=12); self.info_bar.pack(fill=tk.X)
        self.canvas = tk.Canvas(self.root, bg=CANVAS_BG, highlightthickness=0); self.canvas.pack(fill=tk.BOTH, expand=True)

        legend = tk.Frame(self.root, bg=BG); legend.pack(fill=tk.X, padx=10, pady=2)
        for color, label in [(BAR_DEF,"Default"), (BAR_CMP,"Comparing"), (BAR_SWAP,"Swapping"), (BAR_DONE,"Sorted"), (BAR_PIVOT,"Pivot"), (BAR_SEL,"Selected")]:
            tk.Label(legend, bg=color, width=2).pack(side=tk.LEFT, padx=(6,1))
            tk.Label(legend, text=label, bg=BG, fg=TEXT_FG, font=("Courier", 8)).pack(side=tk.LEFT, padx=(0,8))

        tk.Label(self.root, text="Space: pause/resume  |  → : step  |  G: generate  |  S: sort  |  R: reset", bg=BG, fg="#444466", font=("Courier", 8)).pack(pady=2)
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Right>", lambda e: self.step_once())
        self.root.bind("g", lambda e: self.generate_array()); self.root.bind("G", lambda e: self.generate_array())
        self.root.bind("s", lambda e: self.start_sort()); self.root.bind("S", lambda e: self.start_sort())
        self.root.bind("r", lambda e: self.reset()); self.root.bind("R", lambda e: self.reset())
        ttk.Style().theme_use("default")

    def _lbl(self, parent, text): return tk.Label(parent, text=text, bg=PANEL_BG, fg=TEXT_FG, font=("Courier", 10))
    def _stat_lbl(self, parent, text, col):
        lbl = tk.Label(parent, text=text, bg=PANEL_BG, fg=ACCENT, font=("Courier", 10, "bold")); lbl.grid(row=0, column=col, padx=8)
        return lbl

    def _on_algo_change(self): self.info_bar.config(text=ALGO_INFO.get(self.algo_var.get(), ""))

    def generate_array(self):
        self.reset()
        self.array_data = make_array(self.size_var.get(), self.dist_var.get())
        self.draw_bars(self.array_data, [BAR_DEF] * len(self.array_data))

    def draw_bars(self, data, colors):
        c = self.canvas; c.delete("all")
        if not data: return
        cw, ch = c.winfo_width() or 900, c.winfo_height() or 380
        n = len(data)
        max_val = max(data)
        bar_w = cw / n
        pad = max(0.5, bar_w * 0.08)
        for i, val in enumerate(data):
            x0, x1 = i * bar_w + pad, (i + 1) * bar_w - pad
            bar_h = (val / max_val) * (ch - 10)
            c.create_rectangle(x0, ch - bar_h, x1, ch, fill=colors[i], outline="")
            if n <= 30 and bar_h > 14:
                c.create_text((x0+x1)/2, ch - bar_h + 8, text=str(val), fill="#FFFFFF", font=("Courier", 8, "bold"))

    def start_sort(self):
        if self.running and not self.paused: return
        if self.paused: self.toggle_pause(); return
        self.generator = ALGO_GENS[self.algo_var.get()](self.array_data[:])
        self.running = True; self.paused = self.step_mode = False
        self.comparisons = self.swaps = 0; self.start_time = time.time()
        self.gen_btn.config(state=tk.DISABLED); self.sort_btn.config(state=tk.DISABLED); self.pause_btn.config(state=tk.NORMAL)
        self._animate()

    def toggle_pause(self):
        if not self.running: return
        self.paused = not self.paused
        self.pause_btn.config(text="▶ Resume" if self.paused else "⏸ Pause")
        if self.paused:
            self.step_btn.config(state=tk.NORMAL)
            if self._after_id: self.root.after_cancel(self._after_id); self._after_id = None
        else:
            self.step_btn.config(state=tk.DISABLED); self._animate()

    def step_once(self):
        if not self.running: return
        if not self.paused: self.toggle_pause()
        self._do_step()

    def reset(self):
        if self._after_id: self.root.after_cancel(self._after_id); self._after_id = None
        self.running = self.paused = False; self.generator = None
        self.comparisons = self.swaps = 0; self.start_time = None
        self._update_stats(0, 0); self.time_lbl.config(text="Time: —")
        self.gen_btn.config(state=tk.NORMAL); self.sort_btn.config(state=tk.NORMAL); self.pause_btn.config(state=tk.DISABLED); self.step_btn.config(state=tk.DISABLED)
        if self.array_data: self.draw_bars(self.array_data, [BAR_DEF] * len(self.array_data))

    def _animate(self):
        if not self.running or self.paused: return
        self._do_step()

    def _do_step(self):
        if not self.generator: return
        try:
            data, colors, comps, swaps = next(self.generator)
            self.comparisons, self.swaps = comps, swaps
            self.draw_bars(data, colors); self._update_stats(comps, swaps)
            if not self.paused: self._after_id = self.root.after(max(1, self.speed_var.get()), self._animate)
        except StopIteration:
            self.running = self.paused = False
            elapsed = time.time() - self.start_time if self.start_time else 0
            self.time_lbl.config(text=f"Time: {elapsed:.2f}s")
            self.gen_btn.config(state=tk.NORMAL); self.sort_btn.config(state=tk.NORMAL); self.pause_btn.config(state=tk.DISABLED)
            self.root.bell()

    def _update_stats(self, comps, swaps):
        self.cmp_lbl.config(text=f"Comparisons: {comps:,}")
        self.swap_lbl.config(text=f"Swaps: {swaps:,}")
        if self.start_time: self.time_lbl.config(text=f"Time: {time.time() - self.start_time:.2f}s")

if __name__ == "__main__":
    root = tk.Tk()
    SortVisualiser(root)
    root.mainloop()