import os, gzip, re
from block_ids import BLOCK_NAMES
NAME_TO_ID = {v: k for k, v in BLOCK_NAMES.items()}
from block_color import BLOCK_COLORS
from block_textures_top import BLOCK_TEXTURES_TOP
from PIL import Image, ImageEnhance



#==========================
#------- CONSTANTS -------#
#==========================

#WORLD SAVE PATH
savepath = "/home/arcadianvulture/chunk-renderer/world"

#transparent blocks to skip         to see torches add/remove 50
transp_pixels = {0, 6, 24, 30, 32, 37, 38, 39, 40, 50, 55, 63, 65, 66, 68, 69, 75, 76, 77}

skip_textures = {0, 32, 51, 63, 64, 65, 71, 77, 85}
layer_textures = {6, 18, 20, 23, 24, 27, 30, 37, 38, 39, 40, 50, 52, 55, 59, 66, 69, 70, 72, 75, 76, 83}

#water is 8 and 9






#=========================================
#----------- helper functions -----------#
#=========================================


#get the block texture given a block id
#opens the terrain.png image and uses an indexing map to get location, calculates topLeft and bottomRight pixels, and crops new iamge

def get_block_texture(block_id):
    with Image.open("terrain.png") as im:
        texindex = BLOCK_TEXTURES_TOP[block_id]
        trow = texindex // 16
        tcol = texindex % 16
        pixelx = tcol*16
        pixely = trow*16
        topLeft = (pixelx, pixely)
        pixelx2 = pixelx + 16
        pixely2 = pixely + 16
        bottomRight = (pixelx2, pixely2)
        cropTuple = topLeft + bottomRight
        blockTexture = im.crop(cropTuple)
        return blockTexture


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
    transpBlock = 0
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
                transpBlock = block_id
            continue
        solidBlock = block_id
        return solidBlock, transpBlock, waterDepth
    return 0, 0, 0



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


#creates a dictionary where block ID gives blocks top texture
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



#==========================================
#----------- MAPPING FUNCTIONS -----------#
#==========================================

#create map where every block is 1 pixel
def create_pixel_map(transp_pixels):
    
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
#=======================================================================================




"""
chunkdata = chunks_list(savepath)
bounds = bounding_box_chunks(chunkdata)
xwidth = get_width(bounds[0], bounds[1])
zwidth = get_width(bounds[2], bounds[3])
        
img = Image.new(mode='RGB',size=(xwidth*16*16,zwidth*16*16))

# create dictionary
# block id --> block texture
textures = cropped_top_textures()

#fallback image -- magenta
fallback = Image.new('RGB', (16, 16), (255, 0, 255))

for cx, cz, path in chunkdata:


    blocks = load_chunk_blocks(path)
    height = get_chunk_height(blocks)

    for x in range(16):
        for z in range(16):
            block_id = get_top_block(blocks, x, z, height, transp_pixels) #change to transp for textures later

            texture = textures.get(block_id, fallback) #fallback is diamond block because why not

            img.paste(texture, ((cx-bounds[1])*16*16+x*16,(cz-bounds[3])*16*16+z*16))


img.save('outputs/test2.png')

#EXAMPLE OF GETTING TEXTURE FROM BLOCK NAME/ ID
#testblock = 'plantBlue'

#testid = NAME_TO_ID[testblock]
#testTexture = get_block_texture(testid)
#testTexture.save('outputs/test_texture.png')
"""


textures = cropped_top_textures()
fallback = Image.new('RGB', (16, 16), (255, 0, 255))
chunkdata = chunks_list(savepath)

# filter chunks — adjust range to render more or less           #large region around base i used 0 - 60 and -45 - 15
render_chunks = [(cx, cz, path) for cx, cz, path in chunkdata if 0 <= cx <= 60 and -45 <= cz <= 15]

rc_xmin = min(c[0] for c in render_chunks)
rc_xmax = max(c[0] for c in render_chunks)
rc_zmin = min(c[1] for c in render_chunks)
rc_zmax = max(c[1] for c in render_chunks)

width = (rc_xmax - rc_xmin + 1) * 256
height = (rc_zmax - rc_zmin + 1) * 256

img = Image.new('RGB', (width, height))

maxDepth = 0

for cx, cz, path in render_chunks:
    blocks = load_chunk_blocks(path)
    h = get_chunk_height(blocks)

    for x in range(16):
        for z in range(16):
            solidBlockID, transpBlockID, depthWater = get_top_view_blocks(blocks, x, z, h, skip_textures, layer_textures)

            if depthWater > maxDepth:
                maxDepth = depthWater

            solidTexture = textures.get(solidBlockID, fallback)
            transpTexture = textures.get(transpBlockID, fallback)
            waterTexture = textures[8]
            
            #paste only solid texture if no water
            if depthWater == 0:
                img.paste(solidTexture, ((cx - rc_xmin) * 256 + x * 16, (cz - rc_zmin) * 256 + z * 16))

            #if water depth between 0 and 10, render solid block then render darkened water
            elif depthWater > 0:
                solidRGBA = solidTexture.copy().convert('RGBA')
                blackBG = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
                
                # how much of the bottom you can see (fades to black with depth)
                bottomFade = min(depthWater * 0.066, 1.0)
                darkened = Image.blend(solidRGBA, blackBG, bottomFade)
                
                # blend darkened bottom with water texture
                opaqueWater = Image.new('RGBA', (16, 16), (5, 10, 30, 255))
                opaqueWater.paste(waterTexture, (0, 0), waterTexture)
                
                if depthWater > 14:
                    brightness = max(1 - (depthWater - 14) * 0.03, 0.05)
                    opaqueWater = ImageEnhance.Brightness(opaqueWater).enhance(brightness)

                waterRatio = min(0.50 + depthWater * 0.02, 0.98)
                blended = Image.blend(darkened, opaqueWater, waterRatio)
                
                img.paste(blended, ((cx - rc_xmin) * 256 + x * 16, (cz - rc_zmin) * 256 + z * 16))
            
                
            #render transparent block on top of everything
            if transpBlockID != 0:
            
                img.paste(transpTexture, ((cx - rc_xmin) * 256 + x * 16, (cz - rc_zmin) * 256 + z * 16), transpTexture)

img.save('outputs/test_region.png')

print(f"Deepest water: {maxDepth}")
#create_pixel_map(transp_pixels)

































