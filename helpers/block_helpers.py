
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
def get_top_view_blocks(blocks, meta, x, z, height, skipTextures, transpTextures):
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
                metaval = get_metadata_value(meta, x, y, z, height)
                transpBlocks.append((block_id, metaval))
            continue
        elevation = y
        return elevation, block_id, transpBlocks, waterDepth
    return 0, 0, [], 0

def get_metadata_value(meta, x, y, z, height):
    blockIndex = y + z * height + x * height * 16
    byteIndex = blockIndex // 2
    byte = meta[byteIndex]

    if blockIndex % 2 == 0:
        return byte  & 0x0F
    else:
        return (byte >> 4) & 0x0F