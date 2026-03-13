from PIL import Image, ImageEnhance
from data.block_color import BLOCK_COLORS
from helpers.block_helpers import *
from helpers.chunk_helpers import *
from helpers.texture_helpers import *


#---------------------------------------
#create map where every block is 1 pixel
#---------------------------------------

def create_pixel_map(savepath, transp_pixels):
    chunkdata = chunks_list(savepath)
    bounds = bounding_box_chunks(chunkdata)
    xwidth = get_width(bounds[0], bounds[1])
    zwidth = get_width(bounds[2], bounds[3])

    #image based on bounding box size * 16 for a chunk being 16x16 pixels (RGB color space)
    img = Image.new(mode='RGB',size=(xwidth*16,zwidth*16))

    for cx, cz, path in chunkdata:
        blocks = load_chunk_blocks(path)
        height = get_chunk_height(blocks) # world height affects chunk indexing
        for x in range(16):
            for z in range(16):
                block_id = get_top_block(blocks, x, z, height, transp_pixels)
                color = BLOCK_COLORS.get(block_id, (255, 0, 255)) #if color is invalid - make magenta (255, 0 255)

                #calculated chunk + chunk position     bounds[1] is xmin and bounds[3] is zmin
                #cx is max chunk x coordinate, cz max chunk z coordinate
                img.putpixel(((cx-bounds[1])*16+x,(cz-bounds[3])*16+z), color)
    img.save('outputs/test1.png')
    return



#------------------------------------------------
#create top-down world map using topface textures
#transparent blocks, water depth added
#------------------------------------------------

def create_texture_map(savepath,skipTextures,layerTextures,xmin,xmax,zmin,zmax,mode):
    textures = cropped_top_textures()
    fallback = Image.new('RGB', (16, 16), (255, 0, 255)) #if block has no texture - magenta
    chunkdata = chunks_list(savepath)
    waterTexture = textures[8]#preset water texture for quicker rendering

    #image has width & height based on min and max x and z arguments (chunk coordinates)
    render_chunks = [(cx, cz, path) for cx, cz, path in chunkdata if xmin <= cx <= xmax and zmin <= cz <= zmax]
    rc_xmin = min(c[0] for c in render_chunks)
    rc_xmax = max(c[0] for c in render_chunks)
    rc_zmin = min(c[1] for c in render_chunks)
    rc_zmax = max(c[1] for c in render_chunks)
    width = (rc_xmax - rc_xmin + 1) * 256
    height = (rc_zmax - rc_zmin + 1) * 256
    img = Image.new('RGB', (width, height))

    if mode == "night":
        brightnessFactor = 0.36
    elif mode == "day":
        brightnessFactor = 1.0
    else:
        brightnessFactor = 1.0   

    for cx, cz, path in render_chunks:
        blocks = load_chunk_blocks(path)
        h = get_chunk_height(blocks)
        for x in range(16):
            for z in range(16):
                elevation, solidBlockID, transpBlocks, depthWater = get_top_view_blocks(blocks, x, z, h, skipTextures, layerTextures)
                solidTexture = textures.get(solidBlockID, fallback)
                
                #combine chunk coordinates (cx - rc_xmin)*16blocks*16pixels + block coordinates (x*16 pixels)
                pastePosition = ((cx - rc_xmin) * 256 + x * 16, (cz - rc_zmin) * 256 + z * 16)
                
                if mode == "height": #elevation based shading: 144 affects slope, 1.3 and 0.6 are max/min brightness
                    brightnessFactor = max(min((64-elevation)/144 + 1.0, 1.3),0.6)
                shadedTexture = ImageEnhance.Brightness(solidTexture.copy()).enhance(brightnessFactor)

                if depthWater == 0:
                    img.paste(shadedTexture, (pastePosition))

                elif depthWater > 0: #if depth > 0, use water rendering func to combine solid block, watertexture, and depth
                    shadedWater = ImageEnhance.Brightness(waterTexture.copy()).enhance(brightnessFactor)
                    blended = render_water_top_down(shadedTexture, shadedWater, depthWater)
                    img.paste(blended, pastePosition)

                if len(transpBlocks) > 0: #render transparent block on top
                    for texid in reversed(transpBlocks):
                        transpTexture = textures.get(texid, fallback)
                        transpTexture = ImageEnhance.Brightness(transpTexture.copy()).enhance(brightnessFactor)
                        img.paste(transpTexture, pastePosition, transpTexture)

    if mode == "night": #overlay final image with dark blue image ("night-tint")
        nightOverlay = Image.new('RGB', img.size, (4,4,18))
        img = Image.blend(img, nightOverlay, 0.60)
        
    img.save('outputs/test_region.png')
    return