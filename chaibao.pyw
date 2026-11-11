"""Windows desktop companion. Only contact with the cat resets its rest timer."""
import ctypes
import time
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

ASSETS = Path(__file__).resolve().parent / "assets/pet"
WIDTH, HEIGHT = 144, 156
KEY = "#ff00ff"


def activity(seconds):
    if seconds >= 600:
        return "sleep"
    if seconds >= 300:
        return "loaf"
    phase = seconds % 90
    if 35 <= phase < 42:
        return "walk"
    if 65 <= phase < 70:
        return "groom"
    return "sit"


def photo(image):
    image = image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    image.putalpha(image.getchannel("A").point(lambda a: 255 if a >= 96 else 0))
    return ImageTk.PhotoImage(image)


class Companion:
    def __init__(self, root):
        self.root = root
        root.title("柴宝 · 桌宠")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", KEY)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=KEY,
                                highlightthickness=0, borderwidth=0)
        self.canvas.pack()
        self.sprite = self.canvas.create_image(0, 0, anchor="nw")
        atlas = Image.open(ASSETS / "spritesheet.png").convert("RGBA")
        self.frames = {}
        for name, row, count in (("sit", 0, 6), ("right", 1, 4),
                                 ("left", 2, 4), ("groom", 7, 6)):
            self.frames[name] = [photo(atlas.crop((192*i, 208*row, 192*(i+1), 208*(row+1))))
                                 for i in range(count)]
        for name in ("loaf", "sleep"):
            self.frames[name] = [photo(Image.open(ASSETS / f"{name}.png").convert("RGBA"))]
        self.x = max(0, root.winfo_screenwidth() - WIDTH - 24)
        self.y = max(0, root.winfo_screenheight() - HEIGHT - 60)
        self.direction = -1
        self.drag_offset = None
        self.touched = time.monotonic()
        self.menu = tk.Menu(root, tearoff=False)
        self.menu.add_command(label="关闭柴宝", command=root.destroy)
        self.canvas.bind("<Motion>", self.touch)
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Button-3>", self.context_menu)
        self.place()
        self.tick()

    def place(self):
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{self.x}+{self.y}")

    def touch(self, event):
        self.touched = time.monotonic()
        self.canvas.itemconfigure(self.sprite, image=self.frames["sit"][0])

    def press(self, event):
        self.touch(event)
        self.drag_offset = event.x_root - self.x, event.y_root - self.y

    def release(self, event):
        self.drag_offset = None
        self.touch(event)

    def drag(self, event):
        self.touch(event)
        if self.drag_offset:
            self.x = max(0, min(event.x_root - self.drag_offset[0], self.root.winfo_screenwidth() - WIDTH))
            self.y = max(0, min(event.y_root - self.drag_offset[1], self.root.winfo_screenheight() - HEIGHT))
            self.place()

    def context_menu(self, event):
        self.touch(event)
        self.menu.tk_popup(event.x_root, event.y_root)

    def tick(self):
        elapsed = time.monotonic() - self.touched
        state = activity(elapsed)
        if state == "walk":
            limit = max(0, self.root.winfo_screenwidth() - WIDTH)
            if self.x >= limit:
                self.direction = -1
            elif self.x <= 0:
                self.direction = 1
            self.x = max(0, min(limit, self.x + self.direction * 2))
            self.place()
            state = "right" if self.direction == 1 else "left"
        frames = self.frames[state]
        frame = int(elapsed * 6) % len(frames)
        if state == "sit":
            frame = min(5, int(elapsed % 4 * 6))
        self.canvas.itemconfigure(self.sprite, image=frames[frame])
        self.root.after(100, self.tick)


def main():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.restype = ctypes.c_void_p
    mutex = kernel.CreateMutexW(None, False, "Local\\Chaibao_DigitaldeskPet")
    if ctypes.get_last_error() == 183:
        return
    root = tk.Tk()
    Companion(root)
    root.mainloop()
    kernel.CloseHandle(ctypes.c_void_p(mutex))


if __name__ == "__main__":
    main()

