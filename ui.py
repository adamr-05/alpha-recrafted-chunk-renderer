import tkinter as tk
from tkinter import ttk
from mapping import *
import time

currentsavepath = "/home/arcadianvulture/chunk-renderer/world"
skip_textures = {0, 32, 51, 63, 64, 65, 71, 77, 85}
layer_textures = {6, 18, 20, 23, 24, 27, 30, 37, 38, 39, 40, 50, 52, 55, 59, 66, 69, 70, 72, 75, 76, 83}

def on_render():
    create_texture_map(currentsavepath, skip_textures, layer_textures, 20, 30, -30, 5, "height", progress, window, progressLabel)
    time.sleep(0.5)
    window.destroy()

window = tk.Tk()
window.title("Chunk Renderer")
window.geometry("800x600")

label = tk.Label(window, text="Alpha Recrafted Chunk Renderer", font=("Fixedsys", 24))
label.pack(pady=30)

renderButton = tk.Button(window, text="render", command=on_render, font=("Fixedsys", 16), width=20,height=2)
renderButton.pack(pady=80)

progressLabel = tk.Label(window, text="0/0 (0%)", font=("Fixedsys", 14))
progressLabel.pack(pady=5)

style = ttk.Style()
style.configure("Custom.Horizontal.TProgressbar", thickness=40)
progress = ttk.Progressbar(window, length=500, mode='determinate', style="Custom.Horizontal.TProgressbar")
style.configure("Custom.Horizontal.TProgressbar", thickness=30, troughcolor='#2e2d2d', background='#16730f')
progress.pack(pady=30)


window.mainloop()