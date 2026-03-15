import tkinter as tk
from PIL import Image, ImageTk, ImageChops
from font import *
from tkinter import filedialog
from mapping import *

defaultWidth = 854
defaultHeight = 480

skip_textures = {0, 32, 51, 63, 64, 65, 71, 77, 85}
layer_textures = {6, 18, 20, 23, 24, 27, 30, 37, 38, 39, 40, 50, 52, 55, 59, 66, 69, 70, 72, 75, 76, 83}

class ChunkRendererGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Minecraft Chunk Renderer")

        self.canvas = tk.Canvas(self.root, width=defaultWidth, height=defaultHeight)
        self.canvas.pack(fill="both", expand=True)

        self.current_scale = 2
        self.load_raw_assets()
        self.build_scaled_assets()
        self.draw_all()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_move)

    mainMenu_buttonDefs = [
        {"text": "Savepath", "offset": 48, "xoffset": 0, "action": "do_browse_savefile"},
        {"text": "Option 2", "offset": 72, "xoffset": 0, "action": "do_option2"},
        {"text": "Option 3", "offset": 96, "xoffset": 0, "action": "do_option3"},
        {"text": "Render", "offset": 132, "xoffset": 0, "action": "do_render"},
    ]

    def calc_scale(self, width, height):
        s = 1
        while s < 4:
            if width // (s + 1) < 320 or height // (s + 1) < 240:
                break
            s += 1
        return s

    def load_raw_assets(self):
        # load once at original size, never changes
        self.dirt_raw = Image.open('data/dirt.png').convert('RGBA')
        tint = Image.new('RGBA', (16, 16), (64, 64, 64))
        self.dirt_raw = ImageChops.multiply(self.dirt_raw, tint)

        gui_img = Image.open('data/gui.png')
        self.btn_OFF_raw = gui_img.crop((0, 46, 200, 66))
        self.btn_ON_raw = gui_img.crop((0, 66, 200, 86))
        self.btn_SEL_raw = gui_img.crop((0, 86, 200, 106))

        self.char_map, self.char_widths, self.char_crops = load_font('data/default.png')

    def build_scaled_assets(self):
        s = self.current_scale
        tile_size = 16 * s * 2
        self.tile_size = tile_size
        self.scaled_dirt = self.dirt_raw.resize((tile_size, tile_size), Image.Resampling.NEAREST)
        self.dirt_tk = ImageTk.PhotoImage(self.scaled_dirt)

        self.btn_ON = self.btn_ON_raw.resize((200 * s, 20 * s), Image.Resampling.NEAREST)
        self.btn_SEL = self.btn_SEL_raw.resize((200 * s, 20 * s), Image.Resampling.NEAREST)
        self.btn_OFF = self.btn_OFF_raw.resize((200 * s, 20 * s), Image.Resampling.NEAREST)

    def make_button(self, text, base, color=(224, 224, 224)):
        s = self.current_scale
        btn_img = base.copy()
        text_img = render_text(text, self.char_map, self.char_widths, self.char_crops, color=color)
        text_img = text_img.resize((text_img.width * s, text_img.height * s), Image.Resampling.NEAREST)
        tx = (btn_img.width - text_img.width) // 2
        ty = (btn_img.height - text_img.height) // 2
        btn_img.paste(text_img, (tx, ty), text_img)
        return ImageTk.PhotoImage(btn_img)
    
    def on_click(self, event):
        s = self.current_scale
        for btn in self.buttons:
            coords = self.canvas.coords(btn["id"])
            half_w = 100 * s
            half_h = 10 * s
            if coords[0] - half_w <= event.x <= coords[0] + half_w and coords[1] - half_h <= event.y <= coords[1] + half_h:
                getattr(self, btn["action"])()
                break
        
    
    def do_browse_savefile(self):
        path = filedialog.askdirectory(title="Select World Save Path")
        if path:
            self.savepath = path

    def do_option2(self):
        print ("option 2 pressed")
    
    def do_option3(self):
        print ("option 3 pressed")

    def do_render(self):
        create_texture_map(self.savepath, skip_textures, layer_textures, 0, 60, -25, 25, "height")
        self.root.destroy()

    def draw_all(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1:  # canvas not yet drawn
            w = defaultWidth
            h = defaultHeight

        # background
        for y in range(0, h + self.tile_size, self.tile_size):
            for x in range(0, w + self.tile_size, self.tile_size):
                self.canvas.create_image(x, y, image=self.dirt_tk, anchor="nw", tag="bg")

        # buttons
        s = self.current_scale
        centerx = w // 2
        centery = h // 6
        self.buttons = []
        for btn_def in self.mainMenu_buttonDefs:
            normal = self.make_button(btn_def["text"], self.btn_ON)
            hover = self.make_button(btn_def["text"], self.btn_SEL, color=(255, 255, 160))
            bx = centerx + btn_def["xoffset"] * s
            by = centery + btn_def["offset"] * s
            btn_id = self.canvas.create_image(bx, by, image=normal, tag="btn")
            self.buttons.append({"id": btn_id,
                                 "normal": normal, 
                                 "hover": hover, 
                                 "offset": btn_def["offset"], 
                                 "xoffset": btn_def["xoffset"],
                                 "action": btn_def["action"],
                                })  

    def on_mouse_move(self, event):
        if not hasattr(self, 'buttons'):
            return
        s = self.current_scale
        for btn in self.buttons:
            coords = self.canvas.coords(btn["id"])
            half_w = 100 * s
            half_h = 10 * s
            x1 = coords[0] - half_w
            y1 = coords[1] - half_h
            x2 = coords[0] + half_w
            y2 = coords[1] + half_h

            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.canvas.itemconfig(btn["id"], image=btn["hover"])
            else:
                self.canvas.itemconfig(btn["id"], image=btn["normal"])

    def on_resize(self, event):
        new_scale = self.calc_scale(event.width, event.height)
        if new_scale != self.current_scale:
            self.current_scale = new_scale
            self.build_scaled_assets()
            self.draw_all()
        else:
            # just reposition, no rebuild
            self.canvas.delete("bg")
            for y in range(0, event.height + self.tile_size, self.tile_size):
                for x in range(0, event.width + self.tile_size, self.tile_size):
                    self.canvas.create_image(x, y, image=self.dirt_tk, anchor="nw", tag="bg")
            self.canvas.tag_raise("btn")

            s = self.current_scale
            centerx = event.width // 2
            centery = event.height // 6
            for btn in self.buttons:
                bx = centerx + btn["xoffset"] * s
                by = centery + btn["offset"] * s
                self.canvas.coords(btn["id"], bx, by)

    def run(self):
        self.root.mainloop()