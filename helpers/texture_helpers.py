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