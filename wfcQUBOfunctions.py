import numpy as np
import math

# This is the QUBO function. It is the matrix form of a quadratic equation that uses binary variables 
# -> y = xQx'
def qubo(x, Q):
    return x.T @ Q @ x

# Function that 
#   1) cuts out rows and collumns we have pre-seeded with a tile
#   2) adds the new cross interaction qubit terms to the diagonal
def seedMap(Q_, seed_, idc):
    tuple_skips = []
    pad = sum([len(v) for v in seed_]) 
    qInter = np.zeros((np.shape(Q_[0])[0] - pad, np.shape(Q_[0])[0]))
    newQ = np.zeros((np.shape(Q_[0])[0] - pad, np.shape(Q_[0])[1] - pad))
    
    l = len(seed_[0])
    idc_tuple = [[idc[i], i] for i in range(len(idc))]
    idc_tuple = sorted(idc_tuple, key = lambda x: x[0])
    idc_ = [idc_tuple[i][0] for i in range(len(idc_tuple))]
    
    if idc_[0] == 0: 
        idx = idc_
    else: 
        idx = [-l]
        idx += idc_

    tuple_skips = [(idx[i]+l, idx[i+1]) for i in range(len(idx)-1)]
    tuple_skips += [(idx[-1]+l, np.shape(Q_[0])[0])]

    for Q in Q_: 
        idc0 = 0
        qInter = np.zeros((np.shape(Q_[0])[0] - pad, np.shape(Q_[0])[0]))
        for i in range(len(tuple_skips)):
            n0 = tuple_skips[i][0]
            ni = tuple_skips[i][1] 
            
            qInter[idc0:idc0+(ni-n0),:] += Q[n0:ni,:] 
            idc0 += (ni-n0)
            
        idc0 = 0
        for i in range(len(tuple_skips)):
            n0 = tuple_skips[i][0]
            ni = tuple_skips[i][1] 

            newQ[:,idc0:idc0+(ni-n0)] += qInter[:,n0:ni] 
            idc0 += (ni-n0)

    cross = np.zeros((np.shape(Q)[0]))

    for s_ in range(len(idc_tuple)): 
        s = idc_tuple[s_][1]
        seed = seed_[s]
        idc = idc_tuple[s_][0]
        
        for Q in Q_:
            Q_temp = np.zeros(np.shape(Q)[0])
            
            for i in range(l): 
                Q_temp += 2 * Q[idc+i, :] * seed[i]
            
            cross += Q_temp 
     
    check = []
    for i in range(len(tuple_skips)):
        check = np.concatenate((check, cross[tuple_skips[i][0]:tuple_skips[i][1]]))
    Q_append = np.diag(check)
            
    newQ += Q_append

    return newQ 

# Generates Q matrix constraint for legal tile placements
def genLegalQ(num_tiles, ofs, key, H, W):
    tilesInMap = H*W
    # For each tile coordiante in the map we alocate 1 qubit for per tile choice in that coordinate (16 tile hoices in this dungeon example)
    Q = np.zeros((num_tiles*tilesInMap,num_tiles*tilesInMap))

    # Linear index for each tile in the map
    for idx in range(H*W):
        i = idx%W # Map coordinate I
        j = idx//W # Map coordinate J
        xr = idx*num_tiles # Starting index of tile within Q matrix

        # For each of the 4 offsets (N,E,S,W positions relative to current tile)
        for itr in range(len(ofs)):
            o = ofs[itr]
            i_n = i + o[0] # Add offset
            j_n = j + o[1] # Add offset
            
            # If offset coord is within bounds of map still
            if i_n >= 0 and j_n >= 0 and i_n < W and j_n < H:
                # Get index of offset coord in map space and starting index in Q matrix
                idx_n = j_n*W + i_n
                idx_rn = idx_n*num_tiles 

                # Get ket corresponding to offset direction (since we have a matrix for each position)
                k = key[itr]
                i_nt = xr # Starting index of tile being "placed"
                j_nt = idx_rn # Starting index of neighboring tile being checked (N,S,E,W neighbors)
                Q[i_nt:i_nt+num_tiles, j_nt:j_nt+num_tiles] += k # Add the respective nsew key to that 16x16 spce in the Q matrix
    
    return Q

# Generates Q matrix contraints forcing annealer to activate only 1 tile qubit per [i,j]map coordinate
def oneHotQ(num_tiles, H, W, alpha=10):
    mapSize = H*W
    Q = np.zeros((num_tiles*mapSize,num_tiles*mapSize))
    # Constraint is -> +1 on diagonal, and -alpha on all off diagonal terms
    key = (np.identity(num_tiles) - 1)*alpha + np.identity(num_tiles)

    for idx in range(H*W):
        xr = idx*num_tiles # The staritng index of tile [i,j] in Q matrix
        Q[xr:xr+num_tiles, xr:xr+num_tiles] += key # Just add the constraint

    return Q

# Enforces global expectation of a given tile type
def genGlobalProbQ(num_tiles, H, W, global_prob_vec, ab=False):
    # How frequent a tile occurs across an entire map
   
    mapSize = H*W
    Q = np.zeros((num_tiles*mapSize, num_tiles*mapSize))    
    idc = np.arange(0,mapSize*num_tiles, num_tiles) # Starting index of each 
    L = mapSize
    
    # global_prob_vec is of length 16 for our dungeon case
    for p_itr in range(len(global_prob_vec)):
        p = global_prob_vec[p_itr]
        
        # Compute the A and B constants of the global expectation constraint
        if abs(p*L - 0.5) > 0.5 and ab:
            # a singularity exists if (2*p*L - 1) = 0
            A = 1
            B = A / (2*p*L - 1)
        else:
            # A is 0 if (2pl - 1) = 1
            # B = 1, A = 
            B = 1
            A = B * (2*p*L - 1)

        # For the starting index in each tile space
        for j in idc:
            for i in idc:
                if i != j:
                    # If i != j we are looking at the cross interaction term so add -B
                    Q[i+p_itr,j+p_itr] = -B
                else:
                    # We are looking at the self interaction term so add A
                    Q[i+p_itr,j+p_itr] = A
            
    return Q


