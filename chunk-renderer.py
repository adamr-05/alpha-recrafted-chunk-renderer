from mapping import *


#==========================
#------- CONSTANTS -------#
#==========================

#WORLD SAVE PATH
currentsavepath = "/home/arcadianvulture/chunk-renderer/world"

#transparent blocks to skip in block -> pixel map        torch=50
transp_pixels = {0, 6, 24, 30, 32, 37, 38, 39, 40, 50, 55, 63, 65, 66, 68, 69, 75, 76, 77}

#textures to skip vs layer on top (transparency) in block -> topface texture map
skip_textures = {0, 32, 51, 63, 64, 65, 71, 77, 85}
layer_textures = {6, 18, 20, 23, 24, 27, 30, 37, 38, 39, 40, 50, 52, 55, 59, 66, 69, 70, 72, 75, 76, 83}

#water is 8 and 9


#=======================================================================================
#------------------------------------   main   -----------------------------------------
#=======================================================================================

def main():
    create_texture_map(currentsavepath,skip_textures,layer_textures,120,200,-25,25,"height")
    return

main()