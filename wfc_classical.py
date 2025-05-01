
import numpy as np

import torch

import torch.nn as nn

import matplotlib.pyplot as plt

import torch.nn.functional as F

import math

import pygame

from wfcQUBOfunctions import genLegalQ, seedMap, genGlobalProbQ,oneHotQ, qubo

from miscFunctions import *

class stat_metrics():
    def __init__(self, numTiles, sigmas, mapSize):
        self.sigmas = sigmas
        self.numTiles = numTiles
        self.mapSize = mapSize

        # Can specify either a frequency of tile occurance, or an integer amount of tile occurance
        self.tileInts = [ int(sigmas[i][0] * mapSize + 1) if sigmas[i][1] == None else sigmas[i][1] for i in range(numTiles) ]
        if sum(self.tileInts) < mapSize:
            print("Bad ratios.")

        self.bag = sum(self.tileInts)
        
    def update(self, tile):
        if self.tileInts[tile] == 0:
            pass
        else:
            self.tileInts[tile] -= 1
        self.bag -= 1
        if self.bag <= 0:
            self.tileInts = [ int(self.sigmas[i][0] * mapSize + 1)  if self.sigmas[i][1] == None else self.sigmas[i][1] for i in range(self.numTiles) ]
            self.bag = sum(self.tileInts)

    def getLiklihoods(self, idc = None):
        if type(idc) == None: idc = np.arange(self.numTiles)
        c_ = [self.tileInts[c] for c in idc] #self.tileInts[idc[:]]
        if sum(c_) == 0: # If we have no valid tiles 
            c_ = np.ones_like(c_) # Set an equal distribution amongst posibilities 
        return [c/sum(c_) for c in c_]
        
def collapse(wave_map, P = None):
    """
    Takes current wave map, finds the wave of greatest certainty, and chooses a tile to place
    """
    min = 17
    min_v = []
    # Find the wave vector with fewest number of possible tile choices for the UNCOLLAPSES regions 
    for v_ in range(len(wave_map)):
        v = wave_map[v_]
        if len(v[1]) < min and len(v[1]) > 0:   
            min = len(v[1])

    # Make a list of each space with minimum certainty (in case there are multiple)
    min_v = [(ctr, wave_map[ctr][0]) for ctr in range(len(wave_map)) if len(wave_map[ctr][1]) == min] # (index in vector, tile map index)
    # In case of a tie for greatest certainty
    if np.shape(min_v)[0] > 1:
        # Select a random index
        pc = np.random.choice(np.arange(len(min_v))) 
        idx_pair = min_v[pc] # Choose random wave to collapse
        idx_map = idx_pair[1] # Index of wave in MAP SAPCE
        idx_vec = idx_pair[0] # Index of wave in list of WAVES 2 COLLAPSE
        p_wave = P.getLiklihoods(wave_map[idx_vec][1])
        
        tile = np.random.choice(wave_map[idx_vec][1], p=p_wave) # Collapse the wave function (choose a random tile)
        return idx_map, idx_vec, tile

    # Else, do the same thing but no need to randomly choose
    p_t = P.getLiklihoods(wave_map[min_v[0][0]][1])
    tile = np.random.choice(wave_map[min_v[0][0]][1], p=p_t)
    return min_v[0][1], min_v[0][0], tile

def propogate(idx, t, wave_map, map_, key, W):
    """
    idx: int value of map space being set
    t: tile chosen to place at space
    key: key of valid tile placements
    """
    ofs  = [[-1,0], # Left
            [0,-1], # Bot
            [1,0], # Right 
            [0,1]] # Top
    
    # Coordinates of tile being collapsed
    i = idx % W 
    j = idx // W

    t_vec = np.arange(np.shape(key)[1]) # vec of tile IDs
    w = np.zeros((np.shape(key)[1])) # One Hot of tile being placed
    w[t] = 1
    to_update = []
    
    for itr in range(len(ofs)):
        # i,j and linear ID of spaces adjacent to tile being placed
        l = ofs[itr]
        i_ = i+l[0]
        j_ = j+l[1]
        idx_ = i_+j_*W
        
        # If space within map bounds
        if i_ >= 0 and i_ <= W-1:
            if j_ >= 0 and j_ <= W-1:
                k = key[itr] # Get key corresponding to neighbor orientation (NSEW direction relative to tile being placed)
                legal = k[t,:] # # Get vector of legal placements for our tile
                new_wave = t_vec[legal[:]==1] # Get new wave space for neighbor
                to_update.append([idx_, new_wave]) # Add to list to update

    for w in wave_map:
        for w_ in to_update:
            if w_[0] == w[0]:
                w[1] = [tile for tile in w[1] if (tile == w_[1][:]).any()]
   
    map_[idx] = t

def zeroKey(key):
    # Removes dead ends from generation. Makes it possible to fail at generating
    key_ = key
    zeros = [1, 2, 4, 8]
    for k in range(4):
        for i in zeros:
            key_[k,i,:] = 0
            key_[k,:,i] = 0
    
    return key_

def get_image(sheet, frame, numcol, width, height, scale, colorkey):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), (((frame%numcol) * width), (frame//numcol)*height, width, height))
    image = pygame.transform.scale(image, (width * scale, height * scale))
    #image.set_colorkey(colorkey)
    return image

def wfc_(seeding, occp = None):
    map = np.zeros((W*H), np.int64)-1 # Linearly indexed map with values set to -1
    possiblility_vector = [] # Vector of all uncollapsed waves
    collapsing = True

    P_ = occp if occp != None else lambda: None

    for i in range(H*W):
        t = seeding.get(i, None)
        if t != None:
            possiblility_vector.append([i,(t,)])
        else:
            possiblility_vector.append([i,t_])
    
    ctr = 0
    while collapsing and ctr < 50:
        idx_map, idx_vec, t = collapse(possiblility_vector, P_) # Takes wave space, chooses a wave to collapse, and selects a value
        if P_ != None:
            P_.update(t)

        # Remove the collapsed wave from list of uncollapsed waves
        if len(possiblility_vector) > 1:
            possiblility_vector[idx_vec] = possiblility_vector[-1]
            possiblility_vector = possiblility_vector[:-1]
        else:
            collapsing = False 
        # Propogate consequences of newly placed tile to surrounding wave space
        propogate(idx_map, t, possiblility_vector, map, key, W)
    for t in range(len(map)):
        tile = map[t]
        if tile < 0:
            map[t] = 0
    
    return map

if __name__ == '__main__':
    num_tiles = 16
    H = 20
    W = 20
    mapSize = H*W

    # Side 0 connects to side 2 etc...
    links = [[0,2], # Left
            [1,3], # Bot
            [2,0], # Right
            [3,1]] # Top

    key = genDungeonKey(links, num_tiles)
    #key = zeroKey(key)
    
    # Seed map with some tiles
    seeding = {}
    if 0:
        for v in range(10*10):
            i = (v%10)*2
            j = (v//10)*2
            i_ = i+j*20
            seeding[i_] = 0


    tile_idx_dict = {
        0: 15,
        1: 9,
        2: 8,
        3: 11,
        4: 0,
        5: 10,
        6: 3,
        7: 13,
        8:1,
        9:12,
        10:2,
        11:14,
        12:4,
        13:6,
        14:5,
        15:7
    }

    t_ = np.arange(num_tiles)
    sigmas = []
    s = np.random.randint(0,20,16)
    s[0] = 100
    s[5] = 30
    
    s = s / (sum(s))
    for s_ in s:
        sigmas.append([s_, None])   
    
    metrics = stat_metrics(numTiles=num_tiles, sigmas=sigmas, mapSize=mapSize)

    gamewidth = 640
    gameheight = 640
    pygame.init()
    screen = pygame.display.set_mode((gamewidth, gameheight)) 

    clock = pygame.time.Clock() # Create the clock object
    
    sprite_sheet = pygame.image.load("plca.png")
    black = 0, 0, 0

    frame = 3
    numcol = 8
    width = 32
    height = 32
    scale = 1
    colorkey = None
    running = True
    
    fps = 1                                     
    ctr = 0
    # Game loop
    while running:
        map_mapped = []
        # Perform WFC to get integer map 
        m = wfc_(seeding, metrics)
        stat = np.zeros(num_tiles)
        for t in m:
            stat[t] += 1

        for i in range(len(m)): 
            # Map tile IDs from key to tile sheet location
            tile = tile_idx_dict[m[i]]
            # Get tile from sheet
            x = get_image(sprite_sheet, tile, numcol, width, height, scale, colorkey)
            # Create list of pygame Surfaces to draw to screen
            map_mapped.append(x) 

        # Fill screen (clear screen)
        screen.fill(black)
        for i in range(len(map_mapped)):
            x = map_mapped[i]
            # Blit draws each Surface to the screen where labeled. Blit places things super weird heads up
            screen.blit(x,dest=((i//W)*height,(i%W)*width)) # Blit places as [y,x]

        
        
        # Update displays new screen
        pygame.display.update()
        pygame.image.save(screen,"screenshot3.png")
        
        break
        clock.tick(fps) 

            