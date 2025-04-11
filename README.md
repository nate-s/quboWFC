# quboWFC
Re-quantum-iffying the procGen WFC algorithm

Wave Function Collapse using actual quantum computing

I am going to assume that the reader is either 1) already familiar with Wave Function Collapse (WFC) to a degree, or 2) that they have read through the blog post linked [here](https://github.com/mxgmn/WaveFunctionCollapse). You do not need a particularly extensive understanding of WFC to read this, but much of the choices here may not seem particularly interesting without the context of the “original” algorithm and its history. Disclaimer aside, let’s move straight into the exercise of overcomplicating an otherwise very simple and user friendly algorithm. 


To do this we need to explain an idea called Quadratic Unconstrained Binary Optimization, also called a QUBO. Then we can discuss how QUBOs are used to solve problems leveraging quantum hardware. Finally, we can lay out how to take WFC and convert it into a QUBO problem to be solved on said hardware. 
	Now first though, why are we doing this at all? The true answer is that I’m a huge math nerd and think it’s really funny to take a video game algorithm that needlessly appropriated a bunch of quantum physics terminology, and smash it with a mallet back into the realm of quantum physics. The practical answer is that quantum hardware can solve optimization problems that are essentially unsolvable through any other means, and they can do it on the order of milliseconds and faster for our intents and purposes. It also finds the GLOBAL MINIMUM, which does not mean much for us, but is an incredible guarantee in the real of optimization. If a problem can be realistically converted into a form ingestible by a quantum computer, then it likely should be. The disclaimer “realistically” has a lot of important factors behind it but we will discuss those at the end after laying everything out.

QUBO

A QUBO is a mathematical formulation for Binary Optimization problems, or problems where each variable is binary (yes/no) (0/1). We want to find some optimal combination of these variables. A QUBO problem takes the form of:

  y = x1^2*Q1 + x2^2*Q2 + x3^2*Q3 … xN^2*QN  +  2*x1*x2*Q12 + …

Where X_i are binary variables, Q is a set of weights for each choice, and y is the output we are trying to maximize or minimize. In a concrete example we can look at a scenario where we are trying buying the best snack food for a party within a budget:


Soda = X1 = $4
Chips = X2 = $5
Fruits = X3 = $2

Budget = $9

Y = x_soda * q$ + x_chips * q$  + q$ + x_fruits * q$ 

If x_i is a binary variable for “did we buy this item”, and q$_i is the cost, the Y is the total $ amount spent. Accounting for our budget B we can write out the difference between money spent and the budget as:

Diff = ( sum(xi*Qi) - B )^2
->
sum( x_i*q_i )^2 - 2Bsum( x_i*q_i ) + B^2

x_i * (q_i^2 - B) + x_ij * 2*(q_i*q_j) + B^2

Diff = ( sum(xi*Qi) - B )^2

By minimizing the difference we find the optimal combination of items to buy that brings us as close to our budget as possible. This is clearly the Soda and Chips since they total $9, but we could easily include every item in the grocery store’s inventory as a variable and find the global minimum optimal combination over every single item. But to do that we need to convert it into a QUBO, which is of the form:

	x*Q*x’

This is part of the matrix form for a quadratic equation, where x is a [1xN] vector of each binary variable (in our case what items to buy), and Q is the constraint matrix that shapes our whole optimization problem. In this case it is every constant in front of our expanded quadratic equation. 

Diff = ( sum(xi*Qi) - B )^2
-> 
Diff = ( x1*q1 + x2*q2 + x3*q3 - B )^2
Diff = ( x1*q1 + x2*q2 + x3*q3 - B ) * ( x1*q1 + x2*q2 + x3*q3 - B )

After factoring this around ->

Diff = sum_i( (xiQi)^2 ) + 2*sum_i( sum_k( xiQi * xkQk ) ) - 2*sum_i( xiQi*B ) + B^2

Now an important feature about binary equations is that a single variable is equal to it’s square

	1 = 1*1 and 0 = 0*0  therefor  (x = x^2)

Therefore, in our quadratic equation each single term can be squared. When we drop the constants we get:

Diff = sum_i(xi^2 * (Qi^2 - 2*qi*B) ) + 2*sum_i( sum_k( xiQi * xkQk ) ) 

Which is factored into a matrix form as 

Diff = x * Q * x’

Which is coincidentally the exact form of a QUBO problem. In our snack example x is a 1x3 vector where each variable represents our decision to purchase that item. Q is an [NxN] ( [3x3] ) matrix filled with the constants (Qi^2 - 2*qi*B) along the diagonal, and (Qi*Qk) as the cross-interaction coefficients. You can check that the vector x = [1, 1, 0] yields the minimum scalar output, which corresponds to purchasing the Soda and Chips!
	Now this likely seems a very silly over complication. However, keep in mind that we only have 1 constraint, the minimization constraint. One of the great qualities of the QUBO formulation is that the constraint matrix Q is additive with any other equally sized Q matrices. We could create a new optimization constraint, say, the flavor constraint Q_f (so we equitably buy a diverse range of party snack flavors and not just chips). We could then make a new QUBO formulation by adding the two Q matrices together! This means a QUBO problem can have an incredible amount of constraints applied without increasing the memory usage of the problem itself. 

This might be a reasonable point to delve into how a QUBO problem is put onto quantum hardware, which would inevitably bring us to the question of “What is happening under the hood?” However, this is both 1) a digression from WFC and 2) not something I am particularly qualified to explain. I will try to explain some of the quantum physics and science at the end, but for now suffice to say that the benefits of QUBOs on quantum hardware are

  1) A large combinatorial problem can be impossible to solve classically
	2) If we do try, compared to a classical technique like a genetic algorithm the quantum solution can easily be 1e4 times faster. (I have seen this in real professional settings, and it gets faster)
	3) It does this while finding the global minimum. This is an unbelievable promise honestly.

QUBO for WFC

  Let’s first lay out a simple WFC problem. We have 
	1) An empty grid map
	2) A set of tiles we can place in each grid space
	3) A set of adjacency rules dictating what tiles can be placed next to one another

What we are going to do is define a set of binary variables that correspond to a decision to place a single tile type in a single map space. We will be using the following set of 16 tiles to generate a dungeon:

(Show 16 tiles with corresponding qubits q_1-16

For each empty space in the map we are trying to decide which of these 16 tiles we want to place. We therefor assign a binary variable to each tile type for each map space. In an [8x8] size map with 16 tiles this yields 1024 binary variables. On a standard computer each of these variables can be represented by the smaller unit possible, a bit. Since we will be running this on a digital annealer which approximates quantum hardware we will instead represent each of these variables with a quantum bit (a qubit). Any problem set up as a QUBO will return a binary vectors whose qubits represent the minimum/maximum energy of the optimization problem. To set this problem up we need to form 2 constraints:

  1) We cannot place more than 1 tile per map coordinate
	2) A tile can only be placed next to a valid neighboring tile

Without constraint [1] the annealer might activate tile’s qubits per map coordinate i.e. telling us to place a water tile and wall tile in the same space (this is found under the OneHotQ function). To prevent this we need a constraint that makes placing more than 1 tile per space suboptimal. Since the annealer will find the global minimum it will never output a solution that violates this constraint. If we only want one qubit to activate we can write this as:

sum_i( xi ) = 1

For two variables this expands to 				

( 1 - x - y + 2xy )

And for 3

( 1 - x - y - z + 2xy + 2xz + 2yz ) 

Etc… ->

Q = [ 1 -2 -2 -2 … -2]
    [-2  1 -2 -2 … -2]
	  ... 
    [-2 -2 -2 -2 …  1]

As you maybe can see, by activating only a single qubit we get an energy of 1. By activating any 2 qubits we get an energy of 0, any 3 = -4, etc… Since the annealer will find the globally optimal solution to our Q matrix it does not matter how close the optimal answer is to the sub-optimal answers, it will yield the correct solution. The second constraint is equally simple. For each tile type at a given map space [n,m] we need reward the annealer for activating a neighboring qubit if and only if it is a legal tile placement. We should also penalize it if it is an illegal combination (This is done in the genLegalQ function). As a brief example:

For map space [I,j] and tile type k
	q_ij_k

We have map space [0,0], tile type 0
	q_00_0

And map space [1,0], tile type 5
	q_10_5

If it is legal to place tile 5 above tile 0 then the weight w in w * q_00_0 * q_10_5 will be 1, and if not it will be -1. Our Q matrix using these two constraints looks like this:

(Out in the visual Q matrix)

  One their own these two constraints are enough to produces correct maps but they won’t necessarily make exciting maps and we have no control over the generation process. For instance, in the traditional procgen wfc algorithm, one of the things you usually want to implement is a frequency constraint. In example, if a treasure chest only appears once in your demo map then you likely want to generate maps that try to maintain the same treasure chest frequency, else a player would be laden with treasure chests and find your game a little too easy. I’m going to categorize this type of constraint as a flavoring constraint, or, any constraint that affects the style of maps generated.
	My implementation of the frequency constraint is found in the genGlobalProbQ function. The derivation is as follows:

In a map of size NxN the frequency of tile k is sigma_k

  sigma_k = ( # of times tile k is used)  / ( N*N )

Laying out the general quadratic equation just for tile k:

  A * ( q1*q1 + q2*q2 + q3*q3 + … qNN*qNN ) + B * ( q1*q2 + q1*q3 +… q1*qNN + … 				qN-1*QNN ) = E

Constant A has [N] terms and B has N*(N-1) terms. Since we are working with binary variables, the sum of n activated qubits is n, so we can substitute N and N*(N-1) directly:

  A*n + B*n*(n-1) 	 = E
	-> A*n + B*n^2 - B*n	 = E
	-> B*n^2 + n * (A - B)	 = E

This tells us the output of our quadratic for n activated qubits. All we have to do now is find the weights A and B such that activating n qubits gives a frequency of sigma_k = n/(N*N). To do this we can start by finding where the maximum or minimum of the energy function is, which is done by taking the derivative with respect to n and setting equal to zero (wow truly back to calc 1 days):

  dE/dn = 2*B*sigma_k * n + (A - B) = 0

And since we know for our map of size is NxN, the correct number of tiles to use is

  sigma_k = n/(N*N) -> n = sigma_k*( N*N )

Which we can substitute into our derivative to get
	
  2*B*sigma_k * ( N*N ) + (A - B) = 0

We can solve for A:

  A = - B * ( 2 * sigma_k*( N*N ) - 1 ) 

I have decided we can set B arbitrarily to 1 resulting Q matrix that might look like:

(Q matrix for probability constraint)

Now the optimal solution to our QUBO function is one where tile k only occurs with frequency sigma_k! This is an essentially complete solution for procgen WFC, but it’s missing a very specific degree of control necessary for game dev. For the dungeon example we need at least 1 entrance for our player to enter through and we may want to control where that entrance is placed. The thought process for my proposed solution is as follows. We have a set of qubits corresponding to a tile space [0, 0]:

  sum_j( sum_i( qi * qj * Q_ij ) )

Where I and J range from 0->num_tiles. This corresponds to the QUBO expansion for the first tile [0, 0]. We also have the qubits corresponding to all cross activations:

  sum_j’( sum_i( qi * qj’ * Q_ij’ ) ) 

Where j’ ranges from num_tiles->H * W * num_tiles. This corresponds to every other qubit for every other tile space on the map. If we want to pre-seed the first tile with a dungeon entrance (tile # 3), then we end up with a vector 

  v = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Now all cross activation terms take on their seeded values, so for the first qubit we get:

  q1 * qj’ * Q1j’	->  (1/0) * qj’ * Q1j’

And the sum of the cross activation terms becomes:

  sum_j’( 1 * qj’ * Qij’ ) + sum_j’( 0 * qj’ * Qij’ )	

and since a binary variable also equals its square (0 = 0*0 & 1 = 1*1) we will expand this to ->
	
  sum_j’( ( 1 * qj’ * qj’ * Q_ij’ ) ) + sum_j’( ( 0 * qj’ * qj’ * Q_ij’ ) )

Where the 0s and 1s correspond to the seeded qubit vector 
	
  v = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
 
And seeding a specific tile will only affect the weight along the diagonal. We now have 4 constraints in our Q matrix:

  1) Q_one_hot
	2) Q_place_key
	3) Q_frequency
	4) Q_seeded

  -> Q = Q_one_hot + Q_place_key + Q_frequency  + Q_seeded

With this we can generate a tile map where, for each map coordinate, we: will choose only a single tile, will choose a tile that connects legally to it’s neighbors, where each tile occurs as close to a set number of times as possible, and where any map coordinate can be pre-seeded with a tile before generation. This is very cool and potentially very powerful in my opinion. One of the greatest limitations of classical WFC is that, as a sequential decision making algorithm, it’s very slow. And while it’s remarkably simple to implement it can be incredibly tricky to fix incorrectly generated maps. The QUBO method finds solutions to these complex combinatorial problems at very fast speeds that are guaranteed to be correct, so QUBOs run on an annealer are free of both these problems! 

HOWEVER, the tradeoffs are immense. From here on out is a discussion on the limitations of the QUBO problem and how they affect the WFC solution shown so far. The main points are:

  1) memory limitations
	2) Randomness 

The first of these problems is a modern hurdle for all quantum computers. The second of these problems stems from my inability to access a digital annealer at the moment. Either way, as with everything written so far, all comments, criticisms, suggestions, and collaborations are welcome!

1) Memory
	The first and most immediate bottleneck with quantum hardware and software today is how limited it is by memory. A qubit is analogous to an actual bit, and a cutting edge annealer may only have access to around ~5k qubits. Our dungeon problem was building an [8 x 8] map with 16 tile types. This uses 1024 qubits. We clearly will not be generating a Minecraft sized world with this number of variables. We could generate a map of size [17 x 17] using 4624 qubits, but even then we aren’t exactly using a wide array of tile types. Now this isn’t necessarily a problem and it’s definitely not insurmountable. For instance this may not be as restrictive as we might think, after all, Into the Breach takes place on [8 x 8] tile maps and those maps yield an immense amount of gameplay complexity. What if we want to build something along the lines of one of the 2D Zelda maps? We could formulate this as a chunk generation problem and build 1000 [8 x 8] spaces which can be stitched together to make an [800 x 800] sized map. Running these problems on an annealer is fast enough that 1000 solutions is still remarkably fast (and way faster than you could run traditional WFC). The question that remains is: How do you make a compelling world map one [8 x 8] chunk at a time?

2) Randomness
	The point of WFC is to procedurally generate different maps each time. An annealer solves a given QUBO problem. The annealer will therefor return the same solution each time if that solution is the singularly most optimal of all possible combinations. This is not random and not satisfactory for our intents. Conversely however, if two solutions are both globally optimal, the annealer should return one of the two randomly. A QUBO to demonstrate this would be:

	Q = [1   -1]
	    [-1   1]

Since either [1, 0] or [0, 1] are optimal, the annealer should randomly activate one either of the two qubits. However, I can’t test this since I don’t have access to run time on an annealer >:(
This is important to know because depending on how you set up the constraints for a QUBO WFC matrix, any of the legal placed solutions should be optimal and therefore the annealer will return a random map. I am not a quantum physicist though and don’t actually know what that potential randomness will look like. 
