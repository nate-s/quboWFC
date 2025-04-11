import numpy as np
import math

# The misc functions file contains everything not related to the QUBO work itself. These are largely 
# temp functions used just to generate the maps we build the QUBO formulation from and are just placeholders

# Decompose an integer into 8-bit binary form. This is used to generate basic dungeon tiles.
# For each tile, the bits 1-4 correspond to which edge [N,S,E,W] is "filled" in. If N & S are filled,
# the tile is a corridor, if N & E are filled it's a 90 deg corner, if all bits are filled it's a room, etc..
def decomp(x):
    # For 4 bits, the integer range is 0-15
    denom = 2**7
    v = np.zeros(8)
    # For each bit
    for i in range(8):
        # If it's divisible by 2, we activate that bit (i.e. 1 not 0)
        if x // denom: 
            v[i] = 1 # Activate bit
            x = x - denom # Get remainder 
        denom = denom // 2 # Halve remainder for next pass
        
    return v

# Generate a "key matrix" given our tile set
def genDungeonKey(links, num_tiles):
    tiles = []
    # Each tile has 4 adjacency rules for N,S,E,W neighbors. The Key is 4 NxN matrices
    key = np.zeros((4,num_tiles,num_tiles))

    # Get our basic 16 tiles for a dungeon
    for i in range(num_tiles):
        tiles.append(decomp(i)[4:])

    # For each tile we are checking
    for t_ in range(len(tiles)):
        t = tiles[t_]
        # Compare against each tile
        for comp_ in range(len(tiles)):
            comp = tiles[comp_]
            # For each comparison, check all 4 placements positions
            for l in range(len(links)):
                k = key[l]
                # If the touching edge for both tiles == 1 or each == 0, it is a legal placement
                k[t_][comp_] = int(t[links[l][0]]) == int(comp[links[l][1]])

    return key


def vec2im(vec, num_tiles, H, W, t_im):
    im = np.zeros((H*3,W*3))
    c = np.arange(num_tiles).reshape((1,num_tiles))
    for x in range(H*W):
        icr = x*num_tiles   
        icr_v = vec[icr:icr+num_tiles]
        idc = int(c@icr_v)
        t = t_im[idc]
        i = (x%W)*3
        j = (x//W)*3
        im[i:i+3, j:j+3] = t

    return im

