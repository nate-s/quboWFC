# Wave Function Collapse using actual quantum computing and quantum anealers 

You can find the io page [here](https://nate-s.github.io/quboWFC/). This is a WIP. Updates coming soon are 
1) Cool pictures to convey concepts easier
2) Actual generated maps

I am going to assume that the reader is either 1) already familiar with Wave Function Collapse (WFC) to a degree, or 2) that they have read through the blog post linked [here](https://github.com/mxgmn/WaveFunctionCollapse). You do not need a particularly extensive understanding of WFC to read this, but much of the choices here may not seem particularly interesting without the context of the “original” algorithm and its history. Disclaimer aside, let’s move straight into the exercise of overcomplicating an otherwise very simple and user friendly algorithm. 


To do this we need to explain an idea called Quadratic Unconstrained Binary Optimization, also called a QUBO. Then we can discuss how QUBOs are used to solve problems leveraging quantum hardware. Finally, we can lay out how to take WFC and convert it into a QUBO problem to be solved on said hardware. 

Quickly though, why are we doing this at all? The true answer is that I’m a huge math nerd and think it’s really funny to take a video game algorithm that needlessly appropriated a bunch of quantum physics terminology, and smash it with a mallet back into the realm of quantum physics. The practical answer is that quantum hardware can solve optimization problems that are essentially unsolvable through any other means, and they can do it on the order of milliseconds and faster for our intents and purposes. It also finds the __GLOBAL MINIMUM__, which does not mean much for us, but is an incredible guarantee in the realm of optimization. If a problem can be realistically converted into a form ingestible by a quantum computer, then it likely should be. The disclaimer “realistically” has a lot of important factors behind it but we will discuss those at the end after laying everything out.


## QUBO

A QUBO is a mathematical formulation for Binary Optimization problems, or problems where each variable is binary (yes/no) (0/1). We want to find some optimal combination of these variables. A QUBO problem takes the form of:

$$ y = x_1^2a_{1} + x_2^2a_{2} + x_3^2a_{3} … x_N^2a_{N} +  2x_1x_2a_{12} + … $$

Where $$x_i$$ are binary variables, $$a_{ij}$$ is a set of weights for each choice, and $$y$$ is the output we are trying to maximize or minimize. In a concrete example we can look at a scenario where we are want to buy the best snack food for a party within a budget:

| 	Item |	     Cost |
|------------|------------|
|$$x_{soda}$$|$$a_1=$$$4|
|$$x_{chips}$$|$$a_2=$$$5|
|$$x_{fruits}$$|$$a_3=$$$2|

Given these items and cost the binary formula for how much money we spend is:

$$ Y = x_{soda}a_1 + x_{chips}a_2 + x_{fruits}a_3 $$

If $$x_i$$ is a binary variable for “did we buy this item”, and $$a_i$$ is the cost, then Y is the total dollar amount spent. Accounting for our budget B we can write out the difference between money spent and the budget as:

$$ Budget = {\$9} $$

$$ Diff = ( \sum_{i=1}^3x_ia_i - B )^2 $$

<!---
Expanded to
```math
 \sum_{i=1}^3 (x_iq_i)^2 - 2B\sum_{i=1}^3x_iq_i + B^2
```
Factored to
```math
x_i(q_i^2 - B) + x_{ij}2(q_iq_j) + B^2
```
where i != j in the _cross interaction_ terms.
--->

By minimizing the difference we find the optimal combination of items to buy that brings us as close to our budget as possible. This is clearly the Soda and Chips since they total $9, but we could easily include every item in the grocery store’s inventory as a variable and find the optimal combination. To do that however we need to convert the difference equation into a QUBO of the form: <br/><br/>

$$ y = xQx’ $$

$$ y = \begin{bmatrix}x_1 & x_2 & x_3 & ... & x_{N}\end{bmatrix} 
\begin{bmatrix}a_{11} & a_{12} & a_{13} & ... & a_{1N}\\
a_{21} & a_{22} & a_{23} & ... & a_{2N}\\ 
a_{31} & a_{32} & a_{33} & ... & a_{3N}\\ 
  &  & ... &  & \\ 
a_{N1} & a_{N2} & a_{N3} & ... & a_{NN}\end{bmatrix}
\begin{bmatrix}x_1\\
x_2\\ 
x_3\\ 
.\\ 
.\\ 
.\\ 
x_{N}\end{bmatrix} $$


<!---
```math
y = xQx’
```
or 
```math
y = \begin{bmatrix}x_1&x_2&x_3&...&x_{N}\end{bmatrix} 
\begin{bmatrix}a_{11}&a_{12}&a_{13}&...&a_{1N}\\a_{21}&a_{22}&a_{23}&...&a_{2N}\\a_{31}&a_{32}&a_{33}&...&a_{3N}
\\ & &...\\a_{N1}&a_{N2}&a_{N3}&...&a_{NN}\end{bmatrix}
\begin{bmatrix}x_1\\x_2\\x_3\\.\\.\\.\\x_{N}\end{bmatrix} 
```
--->

<br/><br/>
This is the Holy QUBO Equation, it defines the entirity of a QUBO problem, and it is the matrix form of a _quadratic optimization problem_ using _binary variables_. The vector __x__ contains each binary variable in the optimization problem, and the square matrix __Q__ contains the weights for each respective combination of binary variables. The goal is to find what combination of binary variables (0s and 1s) will yield the optimal output __y__ (either the minimum or maximum value). Funny enough, our contrived snack example is an optimization problem built up from binary decision variables! This can be coneverted into a QUBO but first we need to write it out as a quadratic equation.

$$ Diff = ( \sum_{i=1}^{N=3}x_ia_i - B )^2 $$

Writing out the sum gives:

$$ Diff = ( x_1a_1 + x_2a_2 + x_3a_3 - B )^2 $$

Which expands to:

$$ Diff = ( x_1a_1 + x_2a_2 + x_3a_3 - B ) * ( x_1a_1 + x_2a_2 + x_3a_3 - B ) $$

After factoring and writing back into summation form yields:

$$ Diff = \sum_{i=1}^{N=3}\sum_{k=1}^{N=3}x_ia_ix_ka_k - 2\sum_{i=1}^{N=3}x_ia_iB + B^2 $$

Which should look similar to the quadratic equation

$$ y = ax^2 + bx + c $$

However, a special feature about QUBOs is that they only have _second order_ terms. Fortunately _binary variables_ have a unique quality where a variable is equal to its square i.e $$1 = 1x1$$ and $$0 = 0x0$$ therefor $$x = x^2$$. In our binary quadratic equation we will square each first order variable leaving only constants and second order terms. The solution to the optimization problem is also not dependant on the constants so we can drop them giving:

$$ Diff = \sum_{i=1}^{N=3}x_i^2(a_i^2 - 2a_iB) + 2\sum_{i=1}^{N=3}\sum_{k}x_ia_ix_ka_k $$

Which can be written in matrix form as

$$ Diff = xQx' $$

Here, __x__ is a vector of length 3 with a binary variable correpsonding to buying a given snack. __Q__ is a square matrix of size [3x3] with the _self interaction coefficents_ (diagonal terms) $$(a_i^2 - 2a_iB)$$ and _cross interaction coefficients_ (off diagonal terms) $$a_ia_k$$. You can check that the vector x = [1, 1, 0] yields the minimum scalar output which corresponds to purchasing the Soda and Chips!
	
 
Now this likely seems a very silly over complication. Keep in mind however that we only have 1 constraint minimizing budget difference. A great quality of QUBO is that the constraint matrix Q is additive with any other Q matrix of equal size. We could create a new optimization constraint, say, the flavor constraint $$Q_{flavor}$$ so we equitably purchase a diverse range of party snack flavors and not just chips. We could then make a new QUBO formulation by adding the two Q matrices together. This means a QUBO problem can have a large amount of constraints applied without increasing the memory usage of the problem itself (the number of variables). 

This might be a reasonable point to dive into how a QUBO problem is put onto quantum hardware, which would inevitably bring us to the question of “What is happening under the hood?” However, this is both 1) a digression from video game WFC and 2) not something I am particularly qualified to explain. I will try to explain some of the quantum physics and science at the end, but for now suffice to say that the benefits of QUBOs on quantum hardware are as follows:

  1) A large combinatorial problem can be impossible to solve classically
  2) If we try anyway, compared to a classical technique like a genetic algorithm, the quantum solution can easily be 1e4 times faster. (I have seen this in professional settings and it gets faster)
  3) It does this while finding the _global minimum_. This is a wild promise honestly.




## QUBO applied to WFC

Let’s first lay out a simple WFC problem. We have
  1) An empty grid map
  2) A set of tiles we can place in each grid space
  3) A set of adjacency rules dictating what tiles can be placed next to one another

What we are going to do is define a set of binary variables that correspond to a decision to place a _single tile type_ in a _single map space_. We will be using the following set of 16 tiles to generate a dungeon:

(Show 16 tiles with corresponding qubits $$x_1$$ through $$x_{16}$$) 

For each empty space in the map we are trying to decide which of these 16 tiles we want to place. We therefor assign a binary variable to each tile type for each map space. In an [8x8] size map with 16 tiles this yields 1024 binary variables. On a standard computer each of these variables can be represented by the smallest unit possible, a bit. Since we will be running this on something called a _digital annealer_, which approximates quantum hardware, we will instead represent these variables with a _quantum bit_ (a qubit). We will define a qubit in our problem as $$x_{i,j,k}$$ corresponding to a tile type K placed at map coordinate [i,j]. Any problem set up as a QUBO will return a binary vector whose _qubits_ represent the minimum/maximum energy of the optimization problem set up by the __Q__ matrix. To do this for proc gen WFC we need to develop 2 constraints:

  1) We cannot place more than 1 tile per map coordinate
  2) A tile can only be placed next to a valid neighboring tile

Without constraint [1] the annealer could activate multiple qubits per map coordinate i.e. telling us to place a water tile and wall tile in the same space. To prevent this we need a constraint that defines placing more than 1 tile per space as suboptimal (this is found under the oneHotQ function). Since the annealer will find the global minimum it will never output a solution that violates this constraint __IF__ we formulate it correctly. Since we only want one qubit to activate per space we can write this constraint mathematically as:


$$ \sum_{i}^Nx_i = 1 $$


For two variables we write the optimization equation as				


$$ E = ( 1 - x - y + 2xy ) $$


And for 3


$$ E = ( 1 - x - y - z + 2xy + 2xz + 2yz ) $$


Etc. As you can see the cross interaction terms are +2 and the self interaction terms are -1. Since I have abritrarily decided to write this as a _maximization_ problem I swapped the signs making the Q matrix:


$$ Q = \begin{bmatrix} 1 & -2 & -2 & ... & -2\\
-2 & 1 & -2 & ... & -2\\
-2 & -2 & 1 & ... & -2\\
  &  & ... &  & \\ 
-2 & -2 & -2 & ... & 1 \end{bmatrix} $$

<br/>
As you might see, by activating only 1 qubit we get an energy of 1. By activating any 2 qubits we get an energy of 0, any 3 = -4, etc… Since the annealer will find the globally optimal solution to our Q matrix it does not matter how close the optimal answer is to any sub-optimal answers. <br/> <br/>


<img src="{{site.url}}/images/Q%20One%20Hot%20Tile%20Constraint.png" style="display: block; margin: auto;" />


The second constraint (legal neighbor placement) is equally simple. For each tile type at a given map space [i,j] we need to reward the annealer for activating a neighboring qubit if and only if it is a legal tile placement. We should also penalize it if it's an illegal combination (This is done in the genLegalQ function). To demonstrate, let the qubit $$x_{i,j,k}$$ correspond to a tile type K placed at map coordinate [i,j]. Take as example the qubits $$x_{0,0,0}$$ and $$x_{1,0,5}$$. If it's legal to place tile 5 above tile 0 then the cross coefficient $$a$$ in $$ax_{0,0,0}x_{1,0,5}$$ will be 1, and if it's illegal it will be -1. The new Q matrix is comprised of both these constraints 


$$ Q = Q_{oneHot} + Q_{legal} $$


On their own these two constraints are enough to produce _correct_ maps, but they won’t necessarily produce _exciting_ maps, and we have zero control over the generation process. In traditional procgen WFC one of the things a dev usually wants to implement is a _frequency constraint_. If a treasure chest only appears once in the demo map then the generated maps should also try to maintain a similar placement rate, unless the dev wants the player to be lousy with treasure. I’m going to categorize this type of constraint as a _flavoring constraint_, meaning any constraint that affects the style of maps generated (and is found in the genGlobalProbQ function). The derivation is as follows:

In a map of size [NxN], the frequency of tile k is $${\sigma}_k$$, where $${\sigma}_k = ($$ # of times tile k is used $$)/(NN)$$

Laying out the general quadratic equation _just_ for tile k:


$$ y = A(x_1^2 + x_2^2 + x_3^2 + … + x_{NN}^2 ) + B( x_1x_2 + x_1x_3 +… + x_1x_{NN} + … +x_{N-1}x_{NN}) $$

The A matrix has [N] cosntant terms for the diagonal, and the B matrix has N*(N-1) terms for the off-diagonals. Since we are working with binary variables, the sum of n activated qubits is n, so we can substitute N and N*(N-1) directly: <br/>


$$ y = An + Bn(n-1) = An + Bn^2 - Bn = Bn^2 + n(A-B) $$


This quadratic tells us the... energy(?)... for n activated qubits. It doesn't actually mean anything as an equation unless we can make it's minimum/maximum correspond to our desired number of tile placements. This means we have to find the weights A and B such that activating qubits with the frequency $${\sigma}_k = n/(NN)$$ gives the optimal output. To do this we need to find the optimal output in the first place, which we can do by taking the derivative and setting it equal to zero (wow truly back to calc 1 days):


$$ dy/dn = 2Bn + A - B = 0 $$


And since we know for our map of size is [NxN], the correct number of tiles to use is


$$ n = {\sigma}_k(NN) $$

Which we can substitute into our derivative to get

$$ 0 = 2B{\sigma}_k(NN) + A - B $$

We can solve for A:


$$ A = B(1 - 2{\sigma}_k(NN)) $$


I have arbitrarily decided we can set B to 1 resulting Q matrix that might look like:

(Q matrix for probability constraint)

Now the optimal solution to our QUBO function is one where tile k only occurs with frequency $${\sigma}_k$$! This is close to a complete solution for procgen WFC, but it’s missing a very specific degree of control necessary for game dev. In our dungeon example we need at least 1 entrance for our player to enter through and we may want to control where that entrance is placed by _seeding_ that tile. The thought process for my proposed solution is as follows. We have a set of qubits tile space [0, 0]:


$$ \sum_{k=1}^{16}\sum_{k'=1}^{16}x_kx_{k'}a_{kk'} $$


This corresponds to the QUBO expansion for the first tile [0, 0]. We also have the qubits corresponding to all cross activations:


$$ \sum_{k=1}^{16}\sum_{j=17}^{NN}x_kx_ja_{kj} $$


Where $$j$$ spans all remaining cross-coefficients. If we want to seed the first tile with a dungeon entrance (tile # 3), then we end up with a vector 

  v = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Now all cross activation terms take on their seeded values, so for the first qubit we get:


$$ x_1x_ja_{1j} = (0)x_ja_{1j} = (0)x_j^2a_{1j} $$

and the third qubit

$$ x_3x_ja_{3j} = (1)x_ja_{3j} = (1)x_j^2a_{3j} $$

Once again, since a a binary variable's first order term is equal to it's second order term, these can be added to the self activation coefficients of our remaining variables. Therefore, seeding a tile will only affect the weight along the diagonal. We now have 4 constraints in our Q matrix:

  1) $$Q_{oneHot}$$ <br/>
  2) $$Q_{legal}$$ <br/>
  3) $$Q_{\sigma}$$ <br/>
  4) $$Q_{seeded}$$

$$ Q = Q_{oneHot} + Q_{legal} + Q_{\sigma}  + Q_{seeded} $$

<br/><br/>
With this we can generate a tile map where the annealer: will choose only a single tile per grid space, the chosen tile will connect legally to its neighbors, each tile type will occur as close to a set number of times as possible, and any grid space on the map can be seeded. This is very cool in my opinion and potentially very powerful. Classical WFC is extremely limited because it places tiles sequentially which will always pose a major bottleneck. And while it’s remarkably simple to implement it's also incredibly tricky to _fix_ any incorrectly generated maps. QUBOs that are run on an annealer are free of both these problems because they find guaranteed correct solutions to complex problems extremely quickly!



## Problems with QUBOs

HOWEVER, the tradeoffs are immense (monkey's paw curls). From here on out is a discussion on the limitations of the QUBO and how they affect the procgen WFC solution shown so far. The main points are:

  1) memory limitations
  2) Randomness

The first of these problems is a modern hurdle for all quantum computers. The second of these problems stems from my inability to access a digital annealer at the moment. Either way, as with everything written so far, all comments, criticisms, suggestions, and collaborations are welcome!


### 1) Memory

The first and most immediate bottleneck with quantum hardware today is how limited it is by memory. A qubit is analogous to an actual bit, and a cutting edge annealer may only have access to around ~5k qubits. Our dungeon problem was building an [8 x 8] map with 16 tile types. This uses 1024 qubits. We clearly will not be generating a _Minecraft_ sized world with this limited number of variables. We could generate a map of size [17 x 17] using 4624 qubits, but even then we aren’t exactly using a wide array of tile types. Now this isn’t necessarily a problem and it’s definitely not insurmountable. For instance it may not be as restrictive as we might think, after all, _Into the Breach_ takes place on an [8 x 8] grid and those maps provide an immense amount of gameplay complexity. But what if we want to build something along the lines of one of the 2D _Zelda_ maps? We could formulate this as a chunk generation problem, build 1000 [8 x 8] grids, and stitch them together to make an [800 x 800] sized map. Running these problems on an annealer is fast enough that 1000 solutions is still remarkably quick (and way faster than you could run traditional WFC). The question that remains is: How do you make a compelling world one [8 x 8] chunk at a time? (Spoiler I think I might use TF-IDF which comes from information theory and is used in document analysis)

### 2) Randomness

The point of WFC is to procedurally generate a different map every time you run the algorithm. An annealer solves a given QUBO problem. The annealer will therefor return the same solution each time if that solution is the singularly most optimal of all possible combinations. This is not random and not satisfactory for our intents. Conversely, if two solutions are both globally optimal, the annealer should return one of the two randomly. A QUBO to demonstrate this would be:


$$ Q = \begin{bmatrix}1 & -1\\
-1 & 1\end{bmatrix} $$

     
Since either [1, 0] or [0, 1] are optimal the annealer should randomly activate either of the two qubits. I can’t test this however since I don’t have access to run time on an annealer >:( This potential randomness is important to know because depending on how you set up the constraints for a QUBO, any of the "legaly placed solutions" should be optimal. The annealer should therefore return a random map. Since I am not a quantum physicist though and don’t actually know what that potential randomness will look like, is it normaly distributed, is it true random? I DON'T KNOW WHY DID THEY REMOVE THE FREE ANNEALER ACCESS (I get why but I want to make silly game stuff). 

