
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