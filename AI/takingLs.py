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
#Done - Opponent quenen is killed
#Done - Sit on the anthill for three turns 
#Done - 11 food 
#Done - no workers and no food

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
        super(AIPlayer,self).__init__(inputPlayerId, "Taking L's")
        self.childNodes = None
        self.depthLimit = 2
        self.enemyTunnel = None
        self.myFood = None
        self.myTunnel = None

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
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)]

        #nodes = self.findBestMove(currentState, 0)
        me = currentState.whoseTurn
        
        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        foods = getConstrList(currentState, None, (FOOD,))
        if len(foods) > 0:
            if (self.myFood == None):

                self.myFood = foods[0]
                #find the food closest to the tunnel
                bestDistSoFar = 1000 #i.e., infinity
                for food in foods:
                    dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                    if (dist < bestDistSoFar):
                        self.myFood = food
                        bestDistSoFar = dist

        if self.enemyTunnel == None:
            self.enemyTunnel = getConstrList(currentState, 1-me, (TUNNEL,))[0]

        
        if self.enemyTunnel == None:
            self.enemyTunnel = getConstrList(currentState, 1-me, (TUNNEL,))[0]

        nodes = self.findBestMove(currentState, 0)

        bestScore = -1
        i = 0
        bestScoreIndex = 0
        for node in nodes: 
            if node[2] > bestScore:
                bestScore = node[2]
                bestScoreIndex = i
            i += 1
        selectedMove = nodes[bestScoreIndex][0]
        

        return selectedMove
    
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
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass

# a. the Move that would be taken in the given state from the parent node
# b. the state that would be reached by taking that move
# c. an evaluation of this state. When a node is initially created, this will be generated
# using the method you wrote in the previous step. However, it may be updated to a
# more accurate measure as the algorithm proceeds (see below).
# d. (optional) You may also find it helpful to add a reference to the parent node

    def stateEvaluation(self, currentState):  
        # variable initialization
        score = 0
        me = currentState.whoseTurn
        antList = getAntList(currentState, me)
        enemyInv = getEnemyInv(self, currentState)
        #enemyAntList = enemyInv.ants 
        enemyQueen = enemyInv.getQueen
        enemyWorkerList = getAntList(currentState, 1 - me, (WORKER,))

        myInv = getCurrPlayerInventory(currentState)
        myQueen = myInv.getQueen()
        myworkerList = getAntList(currentState, me, (WORKER,))

        ####Automatic game winning or losing####
        
        if myQueen == None or myInv.getAnthill().captureHealth <= 0 or \
            len(myInv.ants) == 1 and myInv.foodCount == 0 or enemyInv.foodCount >= FOOD_GOAL:
            return -1.0

        if enemyQueen == None or enemyInv.getAnthill().captureHealth <= 0 or \
            len(enemyInv.ants) == 1 and enemyInv.foodCount == 0 or myInv.foodCount >= FOOD_GOAL:
            return 1.0

                
        if myQueen.coords == myInv.getAnthill().coords:
            score -= 25

        workerCount = 0
        soldierCount = 0

        for ant in antList:
            if ant.type != QUEEN and ant.type != WORKER and ant.type != SOLDIER:
                return 0
            elif ant.type == WORKER:
                workerCount += 1
                if(ant.carrying):
                    yTunnelDist = abs(self.myTunnel.coords[1] - ant.coords[1])
                    xTunnelDist = abs(self.myTunnel.coords[0] - ant.coords[0])
                    tunnelDist = xTunnelDist + yTunnelDist
                    if tunnelDist < 3:
                        score += 5

                else:
                    yFoodDist = abs(self.myFood.coords[1] - ant.coords[1])
                    xFoodDist = abs(self.myFood.coords[0] - ant.coords[0])
                    foodDist = xFoodDist + yFoodDist
                    if foodDist < 3:
                        score += 5

            elif ant.type == SOLDIER:
                score += 40
                soldierCount += 1
                score += ant.coords[1]

                if len(enemyWorkerList) > 0:
                    enemyWorkerCoords = enemyWorkerList[0].coords
                    dist = approxDist(enemyWorkerList[0],ant.coords)  
                    score -= (dist) * 2
                    adjacentCoords = []
                    adjacentCoords.append((enemyWorkerCoords[0]+1, enemyWorkerCoords[1]))
                    adjacentCoords.append((enemyWorkerCoords[0]-1, enemyWorkerCoords[1]))
                    adjacentCoords.append((enemyWorkerCoords[0], enemyWorkerCoords[1]+1))
                    adjacentCoords.append((enemyWorkerCoords[0], enemyWorkerCoords[1]-1))
                    if ant.coords in adjacentCoords:
                        score += 20
                else:
                    score += 20
                    yDistScore = (-abs(enemyInv.getAnthill().coords[1] - ant.coords[1]) + 10)
                    xDistScore = (-abs(enemyInv.getAnthill().coords[0] - ant.coords[0]) + 10)
                    score += (yDistScore + xDistScore) * 4
                    if ant.coords == enemyInv.getAnthill().coords:
                        score += 20




        if workerCount > 1:
            return 0

        # add 2 to score for each food player has collected
        score += myInv.foodCount * 7

        # add 1 to score for each food your workers are carrying
        for worker in myworkerList:
            if worker.carrying:
                score += 5
        
        return score * 0.01

    # recursive method to find the best move
    def findBestMove(self, currentState, currentDepth):

        currentNodes = []

        childNodes = []
        # expand current node
        legalMoves = listAllLegalMoves(currentState)
        for move in legalMoves:
            nextState = getNextState(currentState, move)
            node = (move, nextState, self.stateEvaluation(nextState))
            currentNodes.append(node)
        
        # sort nodes based on their initial state evaluation score
        # currentNodes.sort(key=lambda x: int(x[2]))

        # base case      
        if currentDepth == self.depthLimit:
            return self.getAvgScore(currentNodes)

        # recursive call to evaluate score based on child nodes
        for node in currentNodes[0:15]:
            state = node[1]
            move = node[0]
            value = self.findBestMove(state, currentDepth+1)
            node = (move, state, value)
            childNodes.append(node)

        if currentDepth > 0:
            return self.getAvgScore(childNodes)
        else:
            return childNodes          
    
    def getAvgScore(self, nodeList):
        avgScore = 0
        for node in nodeList:
            score = self.stateEvaluation(node[1])
            avgScore += score
        avgScore = avgScore / len(nodeList)
        return avgScore




























