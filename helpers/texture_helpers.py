from PIL import Image, ImageEnhance
from data.block_textures_top import BLOCK_TEXTURES_TOP

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


#returns an image blending water texture and block below it based on waterDepth
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

def create_torch_topdown(textures):
    torchTex = textures[50]
    variants = {}
    
    # standing torch (meta 5 and 0) - just the top 2x2
    standing = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    torchTop = torchTex.crop((7, 6, 9, 8))
    standing.paste(torchTop, (7, 7))
    variants[5] = standing
    variants[0] = standing
    
    # wall torch - 2x4 crop (top + stick)
    torchWithStick = torchTex.crop((7, 6, 9, 10))
    
    # meta 1 = east wall - stick points west (left)
    east = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    rotated = torchWithStick.rotate(270, expand=True)
    east.paste(rotated, (0, 7), rotated)
    variants[1] = east
    
    # meta 2 = west wall - stick points east (right)
    west = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    rotated = torchWithStick.rotate(90, expand=True)
    west.paste(rotated, (12, 7), rotated)
    variants[2] = west
    
    # meta 3 = south wall - stick points north (up)
    south = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    rotated = torchWithStick.rotate(180, expand=True)
    south.paste(rotated, (7, 0), rotated)
    variants[3] = south
    
    # meta 4 = north wall - stick points south (down)
    north = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    north.paste(torchWithStick, (7, 12), torchWithStick)
    variants[4] = north
    
    return variants


def create_plant_topdown(textures, blockID, size=14):
    plantTex = textures[blockID]
    topDown = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    shrunk = plantTex.copy().resize((size, size), Image.NEAREST) # type: ignore
    offset = (16 - size) // 2
    topDown.paste(shrunk, (offset, offset), shrunk)
    return topDown


def create_rail_topdown(textures):
    straightTex = textures[66]
    
    with Image.open("terrain.png") as terrainimage:
        row = 112 // 16
        col = 112 % 16
        curveTex = terrainimage.crop((col*16, row*16, col*16+16, row*16+16))
    
    variants = {}
    
    # flat and ascending north-south
    variants[0] = straightTex.copy()
    variants[4] = straightTex.copy()
    variants[5] = straightTex.copy()
    
    # flat and ascending east-west
    variants[1] = straightTex.copy().transpose(Image.Transpose.ROTATE_90)
    variants[2] = straightTex.copy().transpose(Image.Transpose.ROTATE_90)
    variants[3] = straightTex.copy().transpose(Image.Transpose.ROTATE_90)
    
    # curved NW
    variants[6] = curveTex.copy()
    
    # curved NE
    variants[7] = curveTex.copy().transpose(Image.Transpose.ROTATE_270)
    
    # curved SE
    variants[8] = curveTex.copy().transpose(Image.Transpose.ROTATE_180)
    
    # curved SW
    variants[9] = curveTex.copy().transpose(Image.Transpose.ROTATE_90)
    
    return variants