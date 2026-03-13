import os, gzip
from data.block_ids import BLOCK_NAMES
NAME_TO_ID = {v: k for k, v in BLOCK_NAMES.items()}
from data.block_color import BLOCK_COLORS
from data.block_textures_top import BLOCK_TEXTURES_TOP
from PIL import Image, ImageEnhance



#==========================
#------- CONSTANTS -------#
#==========================

#WORLD SAVE PATH
currentsavepath = "/home/arcadianvulture/chunk-renderer/world"

#transparent blocks to skip         to see torches add/remove 50
transp_pixels = {0, 6, 24, 30, 32, 37, 38, 39, 40, 50, 55, 63, 65, 66, 68, 69, 75, 76, 77}

skip_textures = {0, 32, 51, 63, 64, 65, 71, 77, 85}
layer_textures = {6, 18, 20, 23, 24, 27, 30, 37, 38, 39, 40, 50, 52, 55, 59, 66, 69, 70, 72, 75, 76, 83}

#water is 8 and 9



#=========================================
#----------- helper functions -----------#
#=========================================


#detect if chunk uses 128 or 256 world height
#checks a specific block that should be bedrock in 128 world height and should not be in 256 world height

def get_chunk_height(blocks):
    if blocks[128] == 7:
        return 128
    return 256


#grab block id of array given coords and (world height 128 or 256)

def get_block_id(blocks, x, y, z, height):
    return blocks[y + z * height + x * height * 16]


#loops down from top y coordinate to bottom (at x, z) finding first non air block (needs world height limit)

def get_top_block(blocks, x, z, height, transp):
    for y in range(height - 1, -1, -1):
        block_id = get_block_id(blocks, x, y, z, height)
        if block_id not in transp:
            return block_id
    return 0

#loops down from top y coordinate to bottom at (x, z) and returns topmost transparent block and topmost solid block (needs worldheight limit)
def get_top_view_blocks(blocks, x, z, height, skipTextures, transpTextures):
    transpBlocks = []
    waterDepth = 0
    for y in range(height - 1, -1, -1):
        block_id = get_block_id(blocks, x, y, z, height)
        if block_id == 0 or block_id in skipTextures:
            continue
        if block_id == 8 or block_id == 9:
            waterDepth += 1
            continue
        if block_id in transpTextures:
            if waterDepth == 0:
                transpBlocks.append(block_id)
            continue
        solidBlock = block_id
        elevation = y
        return elevation, solidBlock, transpBlocks, waterDepth
    return 0, 0, [], 0


#create array of tuplets with all chunks
#format:  chunks[0][(x,z,path)]         chunks[0][1] gives 0th element z coordinate

def chunks_list(spath):
    chunks = []
    for root, dirs, files in os.walk(spath):
        for f in files:
            if f.startswith('c.') and f.endswith ('.dat'):
                parts = f.split('.')
                x = int(parts[1], 36)
                z = int(parts[2], 36)
                path = os.path.join(root, f)
                chunks.append((x, z, path))
    return chunks


#gives the max and min x and z chunk coordinates for a given chunkslist                     chunks are 16 blocks
#takes a chunkslist given from chunks_list function and returns (xmax, xmin, zmax, zmin)    CHUNK, NOT BLOCK COORDINATES

def bounding_box_chunks(chunks):
    x_coords = [x[0] for x in chunks]
    xmin = (min(x_coords))
    xmax = (max(x_coords))
    z_coords = [z[1] for z in chunks]
    zmin = (min(z_coords))
    zmax = (max(z_coords))
    return xmax, xmin, zmax, zmin


#returns width given max and min

def get_width(max,min):
    width = (max - min) + 1
    return width


#open chunk file and extract usable data
#every byte is a block id

def load_chunk_blocks(path):
    with gzip.open(path) as f:
        data = f.read()

    #usable data begins at 35th byte (beginning is metadata/text)
    blocksStart = 35
    blocks = data[blocksStart:blocksStart + 65536] #65536 is the length of usable chunk data (16*16*255)
    return blocks


#creates a dictionary where block ID gives blocks topface texture
def cropped_top_textures():
    croppedTextures = {}
    with Image.open("terrain.png") as terrainimage:
        for blockID, textureID in BLOCK_TEXTURES_TOP.items():
            texindex = textureID
            trow = texindex // 16
            tcol = texindex % 16
            pixelx = tcol*16
            pixely = trow*16
            topLeft = (pixelx, pixely)
            pixelx2 = pixelx + 16
            pixely2 = pixely + 16
            bottomRight = (pixelx2, pixely2)
            cropTuple = topLeft + bottomRight
            blockTexture = terrainimage.crop(cropTuple)
            croppedTextures[blockID] = blockTexture
    return croppedTextures


def render_water_top_down(solidTexture, waterTexture, depthWater):
    solidRGBA = solidTexture.copy().convert('RGBA')
    blackBG = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
    
    bottomFade = min(depthWater * 0.066, 1.0)
    darkened = Image.blend(solidRGBA, blackBG, bottomFade)
    
    opaqueWater = Image.new('RGBA', (16, 16), (5, 10, 30, 255))
    opaqueWater.paste(waterTexture, (0, 0), waterTexture)
    
    if depthWater > 14:
        brightness = max(1 - (depthWater - 14) * 0.03, 0.05)
        opaqueWater = ImageEnhance.Brightness(opaqueWater).enhance(brightness)

    waterRatio = min(0.50 + depthWater * 0.02, 0.98)
    return Image.blend(darkened, opaqueWater, waterRatio)
    












#============================================================
#-------------------- MAPPING FUNCTIONS --------------------#
#============================================================



#---------------------------------------
#create map where every block is 1 pixel
#---------------------------------------

def create_pixel_map(savepath, transp_pixels):
    
    #using helper functions, get list of chunks and bounding box coordinates
    chunkdata = chunks_list(savepath)
    bounds = bounding_box_chunks(chunkdata)
    xwidth = get_width(bounds[0], bounds[1])
    zwidth = get_width(bounds[2], bounds[3])

    #create new image based on bounding box size * 16 for a chunk being 16x16 pixels (RGB color space)
    img = Image.new(mode='RGB',size=(xwidth*16,zwidth*16))


    #loop across every file in chunkdata
    for cx, cz, path in chunkdata:

        #for each path, load chunkData into blocks array
        blocks = load_chunk_blocks(path)

        #get height of chunk (world height affects indexing)
        height = get_chunk_height(blocks)


        #loop chunk files x and z coordinates
        for x in range(16):
            for z in range(16):
                #only show top block
                block_id = get_top_block(blocks, x, z, height, transp_pixels)

                #get color of obtained block id
                #if invalid, magenta
                color = BLOCK_COLORS.get(block_id, (255, 0, 255))

                #place pixels in calculated chunk + chunk position with specified color
                img.putpixel(((cx-bounds[1])*16+x,(cz-bounds[3])*16+z), color)

    img.save('outputs/test1.png')
    return











#------------------------------------------------
#create top-down world map using topface textures
#transparent blocks, water depth added
#------------------------------------------------

def create_texture_map(savepath,skipTextures,layerTextures,xmin,xmax,zmin,zmax,mode):

    #get array of textures from block id & create list of all chunks
    textures = cropped_top_textures()
    fallback = Image.new('RGB', (16, 16), (255, 0, 255)) #if block has no texture -- magenta
    chunkdata = chunks_list(savepath)


    # Create bounding width for creating image using max and min x and z coordinates
    render_chunks = [(cx, cz, path) for cx, cz, path in chunkdata if xmin <= cx <= xmax and zmin <= cz <= zmax]
    rc_xmin = min(c[0] for c in render_chunks)
    rc_xmax = max(c[0] for c in render_chunks)
    rc_zmin = min(c[1] for c in render_chunks)
    rc_zmax = max(c[1] for c in render_chunks)
    width = (rc_xmax - rc_xmin + 1) * 256
    height = (rc_zmax - rc_zmin + 1) * 256

    #create image
    img = Image.new('RGB', (width, height))

    waterTexture = textures[8]

    #set brightness for day or night
    if mode == "night":
        brightnessFactor = 0.36
    elif mode == "day":
        brightnessFactor = 1.0
    else:
        brightnessFactor = 1.0   

    #loop through every file
    for cx, cz, path in render_chunks:
        #create usable array of chunkData and find worldHeight
        blocks = load_chunk_blocks(path)
        h = get_chunk_height(blocks)

        #loop through all x and z coordinates in chunk
        for x in range(16):
            for z in range(16):
                #get topview blocks for given x and z coordinate
                elevation, solidBlockID, transpBlocks, depthWater = get_top_view_blocks(blocks, x, z, h, skipTextures, layerTextures)

                #convert block IDs to textures
                solidTexture = textures.get(solidBlockID, fallback)
                
                #combine chunk coordinates (cx - rc_xmin)*16blocks*16pixels + block coordinates (x*16 pixels)
                pastePosition = ((cx - rc_xmin) * 256 + x * 16, (cz - rc_zmin) * 256 + z * 16)
                
                #shade solidTexture based on elevation
                if mode == "height":
                    brightnessFactor = max(min((64-elevation)/144 + 1.0, 1.3),0.6)

                shadedTexture = ImageEnhance.Brightness(solidTexture.copy()).enhance(brightnessFactor)


                #paste only solid texture if no water
                if depthWater == 0:
                    img.paste(shadedTexture, (pastePosition))

                #if water depth > 0, use water rendering function to combine solid texture below, water above, and darkness based on depth
                elif depthWater > 0:
                    shadedWater = ImageEnhance.Brightness(waterTexture.copy()).enhance(brightnessFactor)
                    blended = render_water_top_down(shadedTexture, shadedWater, depthWater)
                    img.paste(blended, pastePosition)
                
                #render transparent block on top of everything
                if len(transpBlocks) > 0:
                    for texid in reversed(transpBlocks):
                        transpTexture = textures.get(texid, fallback)
                        transpTexture = ImageEnhance.Brightness(transpTexture.copy()).enhance(brightnessFactor)
                        img.paste(transpTexture, pastePosition, transpTexture)


    if mode == "night":
        nightOverlay = Image.new('RGB', img.size, (4,4,18))
        img = Image.blend(img, nightOverlay, 0.60)
    img.save('outputs/test_region.png')
    return






#=======================================================================================
#------------------------------------   main   -----------------------------------------
#=======================================================================================

def main():
    #create_pixel_map(currentsavepath,transp_pixels)        i did 0 60 -45 15
    create_texture_map(currentsavepath,skip_textures,layer_textures,10,50,-35,5,"night")
    return


main()