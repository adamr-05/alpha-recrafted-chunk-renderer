from PIL import Image

def load_font(filepath):
    charset = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_'abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑªº¿®¬½¼¡«»"
    
    font_img = Image.open(filepath).convert('RGBA')
    pixels = font_img.load()
    
    char_widths = {}
    char_crops = {}
    
    for i in range(256):
        col = i % 16
        row = i // 16
        
        # scan right to left to find rightmost non-transparent pixel
        width = 0
        for x in range(7, -1, -1):
            found = False
            for y in range(8):
                pixel = pixels[col * 8 + x, row * 8 + y] # type: ignore
                if pixel[3] > 0:  # type: ignore
                    found = True
                    break
            if found:
                width = x + 2  # +2 for padding, same as Minecraft
                break
        
        if i == 32:  # space
            width = 4
        
        char_widths[i] = width
        char_crops[i] = font_img.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8))
    
    # build character lookup: character -> grid index
    char_map = {}
    for idx, ch in enumerate(charset):
        char_map[ch] = idx + 32
    
    return char_map, char_widths, char_crops


def render_text(text, char_map, char_widths, char_crops, color=(224, 224, 224), shadow=True):
    # calculate total width
    total_width = 0
    for ch in text:
        if ch in char_map:
            total_width += char_widths[char_map[ch]]
    
    height = 8
    img = Image.new('RGBA', (total_width, height + (1 if shadow else 0)), (0, 0, 0, 0))
    
    # shadow color: (color & 0xFCFCFC) >> 2
    shadow_color = (color[0] // 4, color[1] // 4, color[2] // 4)
    
    if shadow:
        # draw shadow pass at offset (1, 1)
        x = 1
        for ch in text:
            if ch in char_map:
                idx = char_map[ch]
                crop = char_crops[idx]
                tinted = tint_character(crop, shadow_color)
                img.paste(tinted, (x, 1), tinted)
                x += char_widths[idx]
    
    # draw main pass
    x = 0
    for ch in text:
        if ch in char_map:
            idx = char_map[ch]
            crop = char_crops[idx]
            tinted = tint_character(crop, color)
            img.paste(tinted, (x, 0), tinted)
            x += char_widths[idx]
    
    return img


def tint_character(crop, color):
    # replace white pixels with the desired color, keep alpha
    r, g, b = color
    tinted = crop.copy()
    pixels = tinted.load()
    for y in range(8):
        for x in range(8):
            a = pixels[x, y][3]
            if a > 0:
                pixels[x, y] = (r, g, b, a)
    return tinted