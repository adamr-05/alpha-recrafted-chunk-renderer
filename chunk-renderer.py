import gzip
from block_ids import BLOCK_NAMES
from block_color import BLOCK_COLORS
from PIL import Image

with gzip.open('./test_chunk_data/c.0.-1s.dat','rb') as f:
    data = f.read()

idx = data.find(b'Blocks')
blocksStart = idx + 10
blocks = data[blocksStart:blocksStart + 65536]
img = Image.new('RGB', (16,16))


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
        if block_id != 0:
            return block_id
    return 0



height = get_chunk_height(blocks)
for x in range(16):
    for z in range(16):
        block_id = get_top_block(blocks, x, z, height)
        if block_id != 0:
            #print(block_id)
            #print('done')
            color = BLOCK_COLORS.get(block_id, (255, 0, 255))
            img.putpixel((x,z), color)

               
img.save('outputs/output.png')




