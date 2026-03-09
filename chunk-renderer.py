import gzip
from block_ids import BLOCK_NAMES
from block_color import BLOCK_COLORS
from PIL import Image

with gzip.open('./test_chunk_data/c.0.0.dat','rb') as f:
    data = f.read()

print(len(data))

index = data.find(b'Blocks')
blocksStart = index + 10
blocks = data[blocksStart:blocksStart + 65536]
img = Image.new('RGB', (16,16))

for x in range(16):
    row = ""
    for z in range(16):
        for y in range(255,-1,-1):
            index = y + (z*256) + (x*256*16)
            if (blocks[index] != 0):
                row += f"{blocks[index]:3d}  "
                img.putpixel((x, z), BLOCK_COLORS[blocks[index]])
                break
    print(row)
               
img.save('output.png')




