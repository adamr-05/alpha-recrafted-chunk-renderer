import os, gzip

#walk the save directory, get all chunk files in array
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


#open chunk file, extract blocks array
#every byte is a block id
def load_chunk_blocks(path):
    with gzip.open(path) as f:
        data = f.read()
    #usable data begins at 35th byte (beginning is metadata/text)
    blocksStart = 35
    blocks = data[blocksStart:blocksStart + 65536] #65536 is the length of usable chunk data (16*16*255)
    return blocks