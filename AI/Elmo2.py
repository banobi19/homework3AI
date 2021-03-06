import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: This is the homework 2 ai.

# 1. Create a valuation key:

# Automatic Win or lose case: This will result into an automatic -1 or 1
# - 1 means our ai lost and 1 is our ai wins

# Game state cases:
#Done 1) Type of worker: 1, solider/drone/range: 2
#Done 2) For all ants get health based on manual table
#Done 3) 1 per food in storage and currently holding
# 4) my queen get position by enemy is near: -1
# 5) Own ants nearby for adjacent to the anthill: 1
# 6) -1 per food in enemy storage and currently holding
# 7) +3/-3 if we are on enemy anthil with attacking ant or vice versa
# multiple *.01 to make sure that we stay under 1. and 1

# 2. Dictionary
# - the Move that would be taken in the given state from the parent node
# - the state that would be reached by taking that move
# - an evaluation of this state. When a node is initially created, this will be generated
# using the method you wrote in the previous step. However, it may be updated to a
# more accurate measure as the algorithm proceeds (see below).
# - (optional) You may also find it helpful to add a reference to the parent node

# 3. Set the depth level 1 for now but we will change that in the recursive method
# - We are setting a dept level for the amount children nodes we will have in our Dictionary

# 4. A helper method that gets the nodes average score

# 5. getMove() will call our recursive funciton for the current node in the dictionary

# Your recursive method performs these steps:
# a. Generate a list of all possible moves that could be made from the given
# GameState. AIPlayerUtils.py contains code that will do much of this work for
# you. For now, ignore or discard the END_TURN move. We will be performing
# this search as if the opponent was static.
# b. Generate a list of the GameState objects that will result from making each move.
# You will probably find the getNextState() method in AIPlayerUtils.py helpful
# for this part.
# c. Recursive Case: If the depth limit has not been reached, make a recursive call for
# each state in the list and use the result of the call as the new value for this node
# (replacing the value generated by your evaluation method). Don't forget to
# increase the depth by 1 when you make a recursive call!
# d. Use your helper method (see previous step) to assess the overall value of your
# entire list of nodes.
# e. If the depth is greater than zero, return this overall value to the caller. Otherwise,
# return the Move object from the node that has the highest evaluation score

# ALPHA BETA PRUNING NOTES
# Nodes start with a range of [-inf, inf]
# A min node: will start looking at value of children and will pick an upper bound of the value they see. [-inf, min]
# A max node: will start looking at value of children and will pick a lower bound of the max vaue they see. [max, inf]
# To prune: Look at the current range of your node. If it is outside the range of your parent node, then stop evaluating children (i.e. do not expand any further)
# In terms of coding: node[2] can be a int or a tuple. Check type before evaluating.

#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Elmo2")
        self.childNodes = None
        self.depthLimit = 3
        self.elmoId = None

        self.myAntHill = None
        self.myFood = None
        self.myTunnel = None

        self.enemyAntHill = None
        self.enemyTunnel = None
        self.enemyFood = None

        self.maxChildSearch = 25

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        me = currentState.whoseTurn

        # the first time this method is called, the food and tunnel locations
        # need to be recorded in their respective instance variables
        if self.elmoId == None:
            self.setVariables(currentState, me)
        # recursive function to get moves
        infinity = float('inf')
        evalRange = (-infinity, infinity)
        selectedMove = self.findBestMove(currentState, 0, evalRange)

        return selectedMove

    ##
    # findClosest
    # Description: finds the closest target from a set of targets to a given source
    # Parameters:
    #   src: source coord we need things to be close to
    #   targets: list of possible targets (i.e. enemy ants, food)
    #   state: state object (only needed if you want to do stepsToReach > approxDist)
    #
    def findClosest(self, src, targets, state = None):
        if len(targets) < 1:
            return None
        bestTar = targets[0]
        #find the target closest to the source
        bestDistSoFar = 1000 #i.e., infinity
        for target in targets:
            if state == None:
                dist = approxDist(src.coords, target.coords)
            else:
                dist = stepsToReach(state, src.coords, target.coords)
            if (dist < bestDistSoFar):
                bestTar = target
                bestDistSoFar = dist
        return bestTar

    ##
    # setVariables
    # initializes player variables
    #
    def setVariables(self, currentState, me):
        # AI player ID
        self.elmoId = me
        # game board locations
        if self.myTunnel == None:
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]

        if self.myAntHill == None:
            self.myAntHill = getConstrList(currentState, me, (ANTHILL,))[0]

        if self.enemyTunnel == None:
            self.enemyTunnel = getConstrList(currentState, 1-me, (TUNNEL,))[0]

        if self.enemyAntHill == None:
            self.enemyAntHill = getConstrList(currentState, 1-me, (ANTHILL,))[0]

        # food locations
        foods = getConstrList(currentState, None, (FOOD,))
        if len(foods) > 0 and (self.myFood == None):
            self.myFood = self.findClosest(self.myTunnel, foods, currentState)

        if len(foods) > 0 and (self.enemyFood == None):
            self.enemyFood = self.findClosest(self.enemyTunnel, foods, currentState)

        # food distances
        self.myFoodDist = stepsToReach(currentState, self.myFood.coords, self.myTunnel.coords)
        self.enemyFoodDist = stepsToReach(currentState, self.enemyFood.coords, self.enemyTunnel.coords)

    ## findBestMove
    # Description: recursive method to find the best move for a min or max player
    #       node : tuple (move, state, evaluation)
    #       nodes are identified as min or max based on the current player
    #       of that node's state
    # Parameters:
    #   currentState: state of the game to find best move from
    #   currentDepth: current depth in the recursion (max of self.depthLimit)
    #   grandparentEval: the evaluation of the grandparent node for ALPHA BETA pruning
    def findBestMove(self, currentState, currentDepth, grandparentEval):
        # for storing/evaluating nodes
        currentNodes = []
        childNodes = []
        infinity = float('inf')
        parentEval = (-infinity, infinity)

        # expand current node by viewing all legal moves
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves: # evaluate moves & make a node for each --> currentNodes
            # get the resulting state of a move
            nextState = getNextStateAdversarial(currentState, move)

            # remove Elmo's undesirable states
            if nextState.whoseTurn == self.elmoId:
                if (len(getAntList(nextState, self.elmoId, (WORKER,))) > 1):
                    continue
                if (len(getAntList(nextState, self.elmoId, (DRONE,))) > 1):
                    continue
                if (len(getAntList(nextState, self.elmoId, (SOLDIER,))) > 1):
                    continue
                if (len(getAntList(nextState, self.elmoId, (R_SOLDIER,))) > 0):
                    continue

            # start nodes off with an unknown evaluation, or if at depth limit,
            # get utility with evaluation function (and update the range of the parent)
            score = self.stateEvaluation(nextState)
            if currentState.whoseTurn == self.elmoId and score == 1000: # winning move, return it
                return move
            elif not (currentState.whoseTurn == self.elmoId) and score == -1000: # winning move, return it
                return move
            parentEval = self.updateParent(parentEval, score, currentState.whoseTurn)

            # make a node to represent this state
            node = (move, nextState, score)
            currentNodes.append(node)

        # sort nodes based on the desirability of initial state evaluation score

        if currentState.whoseTurn == self.elmoId:
            currentNodes.sort(key=lambda x: x[2], reverse = True) # high scores are good
        else:
            currentNodes.sort(key=lambda x: x[2]) # low scores are good

        # base case: if we are at the depth limit, return the final evaluation score of the level
            # if a min node: final evaluation is the highest min or lowest max score
            # if a max node: final evaluation is the highest max or lowest min score
        if currentDepth >= self.depthLimit:
            node = self.getBestMinimaxNode(currentNodes, currentState.whoseTurn)
            if node == None:
                if currentState.whoseTurn == self.elmoId:
                    return -1000 # very bad score for max
                else:
                    return 1000 # very bad score for min
            else:
                return node[2]

        # Not at depth limit: make recursive call on current nodes
        # To prune: look at the eval given to you by recursive call.
            # 1. Update parentEval with that value.
            # 2. Compare parentEval to grandparentEval.
            # 3. If we are out of range, break out of the loop and stop expanding children.
            # Otherwise, keep expanding
        # for node in currentNodes[0:self.maxChildSearch]:
        for node in currentNodes:

            move = node[0]
            state = node[1]
            score = self.findBestMove(state, currentDepth+1, parentEval)
            if type(score) == Move:
                return move
            node = (move, state, score)
            childNodes.append(node)
            # step 1
            parentEval = self.updateParent(parentEval, score, currentState.whoseTurn)

            # step 2
            if parentEval[1] < grandparentEval[0] or parentEval[0] > grandparentEval[1]:
                # out of range: step 3, prune the rest of the children
                # print('pruned ', len(currentNodes) - len(childNodes), ' nodes')
                break;

        # return either the move or the score for this level of child nodes
        node = self.getBestMinimaxNode(childNodes, currentState.whoseTurn)
        if currentDepth > 0:
            if node == None:
                if currentState.whoseTurn == self.elmoId:
                    return -1000 # very bad for max player
                else:
                    return 1000 # very bad for min player
            return node[2]
        else:
            if node == None:
                move = Move(END, None, None)
            else:
                move = node[0]

            if node[2] == 1000:
                for node in currentNodes:
                    if self.stateEvaluation(node[1]) == 1000:
                        move = node[0]
                        return move

            return move

    ## updateParent
    #
    # Description: update the alpha-beta score range of a parent node based on the
    #   eval score of child node
    # Parameters:
    #   parent: score range of parent
    #   score: score of child
    #   currPlayer: id of current player of parent node (min or max)
    def updateParent(self, parent, score, currPlayer):
        if currPlayer == self.elmoId: # update lower bound
            if score > parent[0]:
                parent = (score, parent[1])
        else: # update upper bound
            if score < parent[1]:
                parent = (parent[0], score)
        return parent

    ## getBestMinimaxNode
    #
    # Description: get the optimal node for the current player
    #   for minimax: min player wants low nodes, max player wants high nodes
    # Return: most optimal node
    def getBestMinimaxNode(self, nodes, currentTurn):
        if currentTurn == self.elmoId: # this is a max node
            nodes.sort(key=lambda x: x[2], reverse = True)

        else: # this is a min node
            nodes.sort(key=lambda x: x[2])
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        #method template, not implemented
        pass


    ## stateEvaluation
    # evaluate the 'goodness' of this state
    # TODO scale evaluation score to a [-1, 1] value
    def stateEvaluation(self, currentState):
        # variable initialization
        score = 0
        me = currentState.whoseTurn
        antList = getAntList(currentState, me)
        myInv = getCurrPlayerInventory(currentState)
        myQueen = myInv.getQueen()

        enemyInv = getEnemyInv(self, currentState)
        enemyQueen = enemyInv.getQueen()
        # determine whether this state should be evaluated as Elmo or opponent
        # and populate 'enemy' values accordingly
        if me == self.elmoId:
            enemyWorkerList = getAntList(currentState, 1 - me, (WORKER,))
            myFood = self.myFood
            myAntHill = self.myAntHill
            myTunnel = self.myTunnel

            enemyFood = self.enemyFood
            enemyAntHill = self.enemyAntHill
            enemyTunnel = self.enemyTunnel
            badScore = -1000
            goodScore = 1000
        else:
            enemyWorkerList = getAntList(currentState, self.elmoId, (WORKER,))
            myFood = self.enemyFood
            myAntHill = self.enemyAntHill
            myTunnel = self.enemyTunnel

            enemyFood = self.myFood
            enemyAntHill = self.myAntHill
            enemyTunnel = self.myTunnel
            badScore = 1000
            goodScore = -1000

        ####Automatic game winning or losing####
        # TODO add scaling
        try:
            winner = getWinner(currentState)
            if winner == 1 or myInv.foodCount == 11:
                return goodScore
            elif winner == 0:
                return badScore
        except:
            pass

        # calculate scores for ants
        workerCount = 0
        soldierCount = 0

        for ant in antList:
            if ant.type == WORKER:
                score += 2 * self.evaluateWorker(ant, myTunnel, myFood)

                # try to incentivize winning the game
                if ant.coords == myTunnel.coords and myInv.foodCount == 10:
                    score += 2 * self.myFoodDist

            elif ant.type == SOLDIER or ant.type == DRONE or ant.type == R_SOLDIER:
                score += self.evaluateSoldier(ant, enemyWorkerList, enemyAntHill)
                if len(self.listAttackableAnts(currentState, ant.coords, UNIT_STATS[ant.type][RANGE])) > 1: #TODO: test
                    score += 5

            elif ant.type == QUEEN:
                # get queen off the anthill, food, or tunnel
                if not (ant.coords == myAntHill.coords or ant.coords == myFood.coords or ant.coords == myTunnel.coords):
                    score += 25
            else: # undesirable ant type
                return 0
        # calculate score for food
        score += 2 * myInv.foodCount * 2 * self.myFoodDist

        # calculate score for queens
        score += myQueen.health * 2
        score -= enemyQueen.health * 2

        # calculate score for Constructions
        score += self.getConstrEvalScore(myAntHill)

        # scale score down
        if currentState.whoseTurn == self.elmoId: # max node
            return score * 0.01
        else: # min node
            return -score * 0.01

    # Helper method to calculate the portion of the evaluation score determined
    # by construction health levels
    def getConstrEvalScore(self, anthill):
        score = 0
        try:
            score += (anthill.captureHealth * 3)
        except:
            pass
        return score

    ## evaluateWorker
    # function to evaluate a worker ant
    #
    def evaluateWorker(self, ant, tunnel, food):
        workerScore = 0
        if ant.carrying:
            # add 5 to score for each food your workers are carrying
            workerScore += self.myFoodDist

            workerScore += self.myFoodDist - approxDist(ant.coords, tunnel.coords)
        else:
            workerScore += self.myFoodDist - approxDist(ant.coords, food.coords)

        return workerScore

    ## evaluateSoldier
    # function to evaluate a soldier ant
    #
    def evaluateSoldier(self, ant, enemyWorkerList, enemyAntHill):
        soldierScore = 0
        soldierScore += 40
        if ant.type == R_SOLDIER:
            soldierScore -= 20

        soldierScore += ant.coords[1]

        # send soldier to attack workers
        if len(enemyWorkerList) > 0:
            enemyWorker = self.findClosest(ant, enemyWorkerList)

            enemyWorkerCoords = enemyWorker.coords
            soldierScore -= (approxDist(ant.coords, enemyWorkerCoords)) * 2
            adjacentCoords = []
            # want soldier to attack enemy: make it sit right next to enemy worker
            adjacentCoords.append((enemyWorkerCoords[0]+1, enemyWorkerCoords[1]))
            adjacentCoords.append((enemyWorkerCoords[0]-1, enemyWorkerCoords[1]))
            adjacentCoords.append((enemyWorkerCoords[0], enemyWorkerCoords[1]+1))
            adjacentCoords.append((enemyWorkerCoords[0], enemyWorkerCoords[1]-1))
            if ant.coords in adjacentCoords:
                soldierScore += 20
        else:
            # no workers, send soldier to enemy anthill (queen will be here for dumb AIs)
            soldierScore += 20
            soldierScore -= (approxDist(ant.coords, enemyAntHill.coords)) * 4
            if ant.coords == enemyAntHill.coords:
                soldierScore += 20

        return soldierScore

    ##
    #listAttackableAnts
    #
    # Parameters:
    #   state: current state of game
    #   attackerLoc: the ant's location who wants to attack
    #   range: the range of the attacking ant
    #
    # Return: the list of enemy ants you are able to attack with given location and range
    ##
    def listAttackableAnts(self, state, attackerLoc, range = 1):
        attackable = listAttackable(attackerLoc, range)
        attackableAnts = []
        for square in attackable:
            ant = getAntAt(state, square)
            if(ant != None and not ant.player == state.whoseTurn):
                attackableAnts.append(ant)
        return attackableAnts

### UNIT TESTS ###
testAnt = AIPlayer("Elmo")
testAnt.elmoId = 0
################################################################################
# getMove(self, currentState):
################################################################################
################################################################################
# findClosest(self, tunnel, foods, state):
################################################################################
tunnel = Construction((2, 1), TUNNEL)
foodList = [Construction((0,4), FOOD), Construction((1,4), FOOD), Construction((2,4), FOOD), Construction((3,4), FOOD)]
inventory1 = Inventory(0, [], [tunnel], 5)
inventory2 = Inventory(1, [], [], 0)
board =[]
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 2 and j == 1:
            loc.constr = tunnel
        if i == 0 and j == 4:
            loc.constr = foodList[0]
        if i == 1 and j == 4:
            loc.constr = foodList[1]
        if i == 2 and j == 4:
            loc.constr = foodList[2]
        if i == 3 and j == 4:
            loc.constr = foodList[3]
        board.append(loc)

inventories = [inventory1, inventory2]
state = GameState(board, inventories, PLAY_PHASE, 0)
closestFood = testAnt.findClosest(tunnel, foodList, state)
if not (closestFood.coords == foodList[2].coords):
    print('- Function findClosest() failed test 1. Food selected at: ', closestFood.coords,
        ', Actual closest food at: ', foodList[2].coords)


################################################################################
# setVariables(self, currentState, me):
################################################################################
myTunnel = Construction((0, 0), TUNNEL)
enemyTunnel = Construction((4, 4), TUNNEL)
myAnthill = Construction((0, 4), ANTHILL)
enemyAnthill = Construction((4, 0), ANTHILL)
foodList = [Construction((0,2), FOOD), Construction((2,2), FOOD), Construction((4,2), FOOD), Construction((3,2), FOOD)]
inventory1 = Inventory(0, [], [myAnthill,myTunnel], 5)
inventory2 = Inventory(1, [], [enemyAnthill, enemyTunnel], 0)
board =[]
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 0 and j == 0:
            loc.constr = myTunnel
        if i == 4 and j == 4:
            loc.constr = enemyTunnel
        if i == 4 and j == 0:
            loc.constr = enemyAnthill
        if i == 0 and j == 4:
            loc.constr = myAnthill
        if i == 0 and j == 2:
            loc.constr = foodList[0]
        if i == 2 and j == 2:
            loc.constr = foodList[1]
        if i == 4 and j == 2:
            loc.constr = foodList[2]
        if i == 3 and j == 2:
            loc.constr = foodList[3]
        board.append(loc)

generalInventory = Inventory(2, [], foodList, 0)
inventories = [inventory1, inventory2, generalInventory]
state = GameState(board, inventories, PLAY_PHASE, 0)
testAnt.setVariables(state, 0)
if not (testAnt.myTunnel.coords == myTunnel.coords):
    print('- Function setVariables() failed test 1. Tunnel found at: ', testAnt.myTunnel.coords,
        ', Actual tunnel at: ', myTunnel.coords)
if not (testAnt.enemyTunnel.coords == enemyTunnel.coords):
    print('- Function setVariables() failed test 2. Enemy tunnel found at: ', testAnt.enemyTunnel.coords,
        ', Actual tunnel at: ', enemyTunnel.coords)
if not (testAnt.myAntHill.coords == myAnthill.coords):
    print('- Function setVariables() failed test 3. Anthill found at: ', testAnt.myAntHill.coords,
        ', Actual anthill at: ', myAnthill.coords)
if not (testAnt.enemyAntHill.coords == enemyAnthill.coords):
    print('- Function setVariables() failed test 4. Enemy Anthill found at: ', testAnt.enemyAntHill.coords,
        ', Actual anthill at: ', enemyAnthill.coords)
if not (testAnt.myFoodDist == 2):
    print('- Function setVariables() failed test 5. Found food distance: ', testAnt.myFoodDist,
        ', Actual food distance = 2')
if not (testAnt.enemyFoodDist == 2):
    print('- Function setVariables() failed test 6. Found food distance: ', testAnt.enemyFoodDist,
        ', Actual food distance = 2')
################################################################################
# findBestMove(self, currentState, currentDepth):
################################################################################
################################################################################
# getBestScore(self, nodeList):
################################################################################
nodes1 = [(None, GameState(None,None,None,0), 0), (None, GameState(None,None,None,0), 110),
        (None, GameState(None,None,None,0), -30), (None, GameState(None,None,None,0), 12), (None, GameState(None,None,None,0), 1),
        (None, GameState(None,None,None,0), 46), (None, GameState(None,None,None,0), 15), (None, GameState(None,None,None,0), 15.1),
        (None, GameState(None,None,None,0), 15), (None,GameState(None,None,None,0), 100)]
nodes2 = []
bestScore1 = testAnt.getBestMinimaxNode(nodes1, 0)
bestScore2 = testAnt.getBestMinimaxNode(nodes2, 0)
if not (bestScore1[2] == 110):
    print('- Function getBestMinimaxNode() failed test 1. Desired score: 110. Found score: ', bestScore1)
if not (bestScore2 == None):
    print('- Function getBestMinimaxNode() failed test 2. Desired Score: -1000. Found score: ', bestScore2)

################################################################################
# stateEvaluation(self, currentState):
################################################################################
# check win condition

# check moving with food
myTunnel = Construction((2, 2), TUNNEL)
enemyTunnel = Construction((2, 4), TUNNEL)
myAnthill = Construction((0, 0), ANTHILL)
myAnthill.captureHealth = 3
enemyAnthill = Construction((3, 4), ANTHILL)
enemyAnthill.captureHealth = 3
grassList = [Construction((2, 1), GRASS), Construction((3, 1), GRASS)]
foodList = [Construction((2,0), FOOD)]
worker1 = Ant((0,1), WORKER, 0)
myQueen = Ant((0, 4), QUEEN, 0)
enemyQueen = Ant((1, 4), QUEEN, 1)
inventory1 = Inventory(0, [worker1, myQueen], [myAnthill,myTunnel], 5)
inventory2 = Inventory(1, [enemyQueen], [enemyAnthill, enemyTunnel], 4)
testAnt.foodDist = 2
testAnt.myAntHill = myAnthill
testAnt.myFood = foodList[0]
testAnt.myTunnel = myTunnel

testAnt.enemyAntHill = enemyAnthill
testAnt.enemyTunnel = enemyTunnel
testAnt.enemyFood = foodList[0]
board =[]
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 2 and j == 2:
            loc.constr = myTunnel
        if i == 2 and j == 4:
            loc.constr = enemyTunnel
        if i == 3 and j == 4:
            loc.constr = enemyAnthill
        if i == 0 and j == 0:
            loc.constr = myAnthill
        if i == 2 and j == 1:
            loc.constr = grassList[0]
        if i == 3 and j == 1:
            loc.constr = grassList[1]
        if i == 0 and j == 1:
            loc.constr = worker1
        if i == 0 and j == 4:
            loc.constr = myQueen
        if i == 1 and j == 4:
            loc.constr = enemyQueen
        board.append(loc)

generalInventory = Inventory(2, grassList, foodList, 0)
inventories = [inventory1, inventory2, generalInventory]
state = GameState(board, inventories, PLAY_PHASE, 0)
score0 = testAnt.stateEvaluation(state)
    # now move to closer to food
coords1 = (1,0)
state1 = getNextState(state, Move(MOVE_ANT, [worker1.coords, coords1], None))
score1 = testAnt.stateEvaluation(state1)
    # or away from food
coords2 = (1,1)
state2 = getNextState(state, Move(MOVE_ANT, [worker1.coords, coords2], None))
score2 = testAnt.stateEvaluation(state2)
    # now move on to food from state 1
state3 = getNextState(state1, Move(MOVE_ANT, [coords1, foodList[0].coords], None))
score3 = testAnt.stateEvaluation(state3)
    # now move on toward dropoff from state3
coords4 = (2, 1)
state4 = getNextState(state3, Move(MOVE_ANT, [foodList[0].coords, coords4], None))
score4 = testAnt.stateEvaluation(state4)
    # or move from dropoff
state5 = getNextState(state3, Move(MOVE_ANT, [foodList[0].coords, coords2], None))
score5 = testAnt.stateEvaluation(state5)
    # now move on to dropoff from state4
state6 = getNextState(state4, Move(MOVE_ANT, [coords4, myTunnel.coords], None))
score6 = testAnt.stateEvaluation(state6)
    # now end the turn after state6
state7 = getNextState(state6, Move(END, None, None))
score7 = testAnt.stateEvaluation(state7)

if not (score1 > score0 and score2 > score0 and score1 > score2): # not carrying, moving toward food
    print('- Function stateEvaluation() failed test 1. Score 0: ', score0, ' Score 1: ', score1,
            ', Score 2: ', score2)
if not (score3 > score1): # not carrying, moving on to food
    print('- Function stateEvaluation() failed test 2. Score 3: ', score3, ', Score 1: ', score1)
if not (score4 > score3 and score5 == score3 and score4 > score5): # carrying, moving away from food
    print('- Function stateEvaluation() failed test 3. Score 3: ', score3, ' Score 5: ', score5,
            ', Score 4: ', score4)
if not (score6 > score4): # carrying, moving on to drop off
    print('- Function stateEvaluation() failed test 4. Score 4: ', score4, ' Score 6: ', score6)
#note: this should be same because getNextState ignores end of turn actions
if not (score6 == score7): # ending turn
    print('- Function stateEvaluation() failed test 5. Score 6: ', score6, ' Score 7: ', score7)

################################################################################
# evaluateWorker(self, ant, tunnel, food):
################################################################################
# food & dropoff adjacent
worker1 = Ant((0,0), WORKER, 0) # further from food
worker2 = Ant((0,1), WORKER, 0) # on tunnel next to food
worker3 = Ant((1,1), WORKER, 0) # has food on food next to tunnel
worker4 = Ant((1,0), WORKER, 0) # has food on further from tunnel
worker3.carrying = True
worker4.carrying = True
tunnel = Construction((0, 1), TUNNEL)
food = Construction((1,1), FOOD)
testAnt.myFoodDist = 1

score1 = testAnt.evaluateWorker(worker1, tunnel, food)
score2 = testAnt.evaluateWorker(worker2, tunnel, food)
score3 = testAnt.evaluateWorker(worker3, tunnel, food)
score4 = testAnt.evaluateWorker(worker4, tunnel, food)

if not (score2 > score1):
    print('- Function evaluateWorker() failed test 1. Worker further from food score: ', score1,
        ', Worker on closer to food score: ', score2)
if not (score3 > score4):
    print('- Function evaluateWorker() failed test 2. Worker further from tunnel: ', score4,
        ', Worker on closer to tunnel: ', score3)

# food & dropoff 2 steps apart
worker1 = Ant((1,1), WORKER, 0) # further from food
worker2 = Ant((2,1), WORKER, 0) # on tunnel next to food
worker3 = Ant((2,2), WORKER, 0) # has food on food next to tunnel
worker4 = Ant((3,2), WORKER, 0) # has food on further from tunnel
tunnel = Construction((1, 1), TUNNEL)
food = Construction((3,2), FOOD)
testAnt.myFoodDist = 3

score1 = testAnt.evaluateWorker(worker1, tunnel, food)
score2 = testAnt.evaluateWorker(worker2, tunnel, food)
score3 = testAnt.evaluateWorker(worker3, tunnel, food)
score4 = testAnt.evaluateWorker(worker4, tunnel, food)
if not (score4 > score3 and score3 > score2 and score2 > score1):
    print('- Function evaluateWorker() failed test 3. Score 1: ', score1, ', Score 2: ', score2,
        ', Score 3: ', score3, ', Score4: ', score4)

worker1.carrying = True
worker2.carrying = True
worker3.carrying = True
worker4.carrying = True
score5 = testAnt.evaluateWorker(worker1, tunnel, food)
score6 = testAnt.evaluateWorker(worker2, tunnel, food)
score7 = testAnt.evaluateWorker(worker3, tunnel, food)
score8 = testAnt.evaluateWorker(worker4, tunnel, food)
if not (score8 < score7 and score7 < score6 and score6 < score5):
    print('- Function evaluateWorker() failed test 4. Score 5: ', score5, ', Score 6: ', score6,
        ', Score 7: ', score7, ', Score8: ', score8)

# worker far from food
worker1 = Ant((1,1), WORKER, 0)
worker2 = Ant((2,3), WORKER, 0)
tunnel = Construction((0, 0), TUNNEL)
food = Construction((4,3), FOOD)
testAnt.myFoodDist = 7

score1 = testAnt.evaluateWorker(worker1, tunnel, food)
score2 = testAnt.evaluateWorker(worker2, tunnel, food)
if not (score2 > score1):
    print('- Function evaluateWorker() failed test 5. Score 1: ', score1, ', Score 2: ', score2)

worker1.carrying = True
worker2.carrying = True
score3 = testAnt.evaluateWorker(worker1, tunnel, food)
score4 = testAnt.evaluateWorker(worker2, tunnel, food)
if  not (score3 > score4):
    print('- Function evaluateWorker() failed test 6. Score 3: ', score3, ', Score 4: ', score4)

################################################################################
# evaluateSoldier(self, ant, enemyWorkerList, enemyAntHill):
################################################################################
################################################################################
    ## UNIT TEST FOR listAttackableAnts(state, attackerLoc, range = 1)
################################################################################
# test no attackableAnts
board = []
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        board.append(loc)
inventory0 = Inventory(0, [], None, None)
inventory1 = Inventory(1, [Ant((2,2), SOLDIER, 0)], None, None)
inventories = [inventory0, inventory1]
testState1 = GameState(board, inventories, PLAY_PHASE, 1)

attackable = testAnt.listAttackableAnts(testState1, (2,2))
if not len(attackable) == 0:
    print('- Function listAttackableAnts() failed. Input: state = ', testState1, ', '
            'location = (2,2); Output: ', attackable)

# test 1 ant
board = []
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 2 and j == 3:
            loc.ant = Ant((i,j), WORKER, 0)
        board.append(loc)
inventory0 = Inventory(0, [Ant((2,3), WORKER, 0)], None, None)
inventory1 = Inventory(1, [Ant((2,2), SOLDIER, 0)], None, None)
inventories = [inventory0, inventory1]
testState2 = GameState(board, inventories, PLAY_PHASE, 1)

attackable = testAnt.listAttackableAnts(testState2, (2,2))
if not len(attackable) == 1 or not attackable[0].type == WORKER:
    print('- Function listAttackableAnts() failed. Input: state = ', testState2, ', '
            'location = (2,2); Output: ', attackable)

# test 2 ants
board = []
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 2 and j == 3:
            loc.ant = Ant((i,j), WORKER, 0)
        if i == 2 and j == 1:
            loc.ant = Ant((i,j), WORKER, 0)
        board.append(loc)
inventory0 = Inventory(0, [Ant((2,3), WORKER, 0), Ant((2,1), WORKER, 0)], None, None)
inventory1 = Inventory(1, [Ant((2,2), SOLDIER, 0)], None, None)
inventories = [inventory0, inventory1]
testState3 = GameState(board, inventories, PLAY_PHASE, 1)

attackable = testAnt.listAttackableAnts(testState3, (2,2))
if not len(attackable) == 2:
    print('- Function listAttackableAnts() failed. Input: state = ', testState3, ', '
            'location = (2,2); Output: ', attackable)

# test range 2
board = []
for i in range (0,5):
    for j in range (0,5):
        loc = Location((i,j))
        if i == 2 and j == 3:
            loc.ant = Ant((i,j), WORKER, 0)
        if i == 2 and j == 0:
            loc.ant = Ant((i,j), WORKER, 0)
        board.append(loc)
inventory0 = Inventory(0, [Ant((2,3), WORKER, 0), Ant((2,0), WORKER, 0)], None, None)
inventory1 = Inventory(1, [Ant((2,2), SOLDIER, 0)], None, None)
inventories = [inventory0, inventory1]
testState4 = GameState(board, inventories, PLAY_PHASE, 1)

attackable = testAnt.listAttackableAnts(testState4, (2,2), 2)
if not len(attackable) == 2:
    print('- Function listAttackableAnts() failed. Input: state = ', testState4, ', '
            'location = (2,2); Output: ', attackable)
