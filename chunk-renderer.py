import os, gzip, re
from block_ids import BLOCK_NAMES
from block_color import BLOCK_COLORS
from PIL import Image

#----------- helper functions -----------#

#detect if chunk uses 128 or 256 world height
#checks a specific block that should be bedrock in 128 world height and should not be in 256 world height
def get_chunk_height(blocks):
    if blocks[128] == 7:
        return 128
    return 256

#grab block id of array given coords and (world height 128 or 256)
def get_block(blocks, x, y, z, height):
    return blocks[y + z * height + x * height * 16]


#loops down from top y coordinate to bottom (at x, z) finding first non air block (needs world height limit)
def get_top_block(blocks, x, z, height):
    for y in range(height - 1, -1, -1):
        block_id = get_block(blocks, x, y, z, height)
        if block_id not in transp:
            return block_id
    return 0

#----------- ---------------- -----------#





#WORLD SAVE PATH
savepath = "/home/arcadianvulture/chunk-renderer/world"

#transparent blocks to skip         to see torches add/remove 50
transp = {0, 6, 24, 30, 32, 37, 38, 39, 40, 50, 55, 63, 65, 66, 68, 69, 75, 76, 77}

#==================================================================================
#create array of tuplets
#format:  chunks[0][(x,z,path)]         chunks[0][1] gives 0th element z coordinate
#==================================================================================
chunks = []
for root, dirs, files in os.walk(savepath):
    for f in files:
        if f.startswith('c.') and f.endswith ('.dat'):
            parts = f.split('.')
            x = int(parts[1], 36)
            z = int(parts[2], 36)
            path = os.path.join(root, f)
            chunks.append((x, z, path))

#----------------------------------------------------------------------------------
#get image size
#----------------------------------------------------------------------------------
x_coords = [x[0] for x in chunks]
xmin = (min(x_coords))
xmax = (max(x_coords))
z_coords = [z[1] for z in chunks]
zmin = (min(z_coords))
zmax = (max(z_coords))

xwidth = xmax-xmin + 1
zwidth = zmax-zmin + 1

#create 2d image of width and height of worldsave
img = Image.new(mode='RGB',size=(xwidth*16,zwidth*16))


for cx, cz, path in chunks:

    #put usable chunk data in array "blocks"
    #format:    blocks[0] = (byte of block id)
    with gzip.open(path) as f:
        data = f.read()
    idx = data.find(b'Blocks')
    blocksStart = idx + 10
    blocks = data[blocksStart:blocksStart + 65536]

    #get height (256 or 128...use different indexing methods)
    height = get_chunk_height(blocks)


    for x in range(16):
        for z in range(16):
            block_id = get_top_block(blocks, x, z, height)
            color = BLOCK_COLORS.get(block_id, (255, 0, 255))

            img.putpixel(((cx-xmin)*16+x,(cz-zmin)*16+z), color)


img.save('outputs/test1.png')










#put invidual file in data var

#open chunk file, name it "f", and use "f.read()", setting data variable to content in file

# with gzip.open('./test_chunk_data/c.0.-1s.dat','rb') as f:
#     data = f.read()





#create array of usable chunk data (not parsed)

#index to start searching chunk data  (first 10 chars are text/info)

# idx = data.find(b'Blocks')
# blocksStart = idx + 10
# #blocks is chunk file from start index to end
# blocks = data[blocksStart:blocksStart + 65536]




#find height of current chunk

# height = get_chunk_height(blocks)

#create image with RGB color space, 16x16 pixels
# img = Image.new(mode='RGB', size=(16,16))


# for x in range(16):
#     for z in range(16):
#         block_id = get_top_block(blocks, x, z, height)
#         if block_id != 0:
#             #print(block_id)
#             #print('done')
#             color = BLOCK_COLORS.get(block_id, (255, 0, 255))
#             img.putpixel((x,z), color)

               
# img.save('outputs/output.png')




