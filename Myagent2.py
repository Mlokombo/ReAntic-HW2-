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
# Node Class
# Description: Represents a node in the search tree.
##
class Node:
    def __init__(self, move, state, depth, evaluation, parent):
        self.move = move
        self.state = state
        self.depth = depth
        self.evaluation = evaluation
        self.parent = parent

    def __repr__(self):
        return f"Node(move={self.move}, depth={self.depth}, evaluation={self.evaluation})"

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
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
        super(AIPlayer,self).__init__(inputPlayerId, "Random2")
   
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
        # Create a list of legal moves
        moves = listAllLegalMoves(currentState)
       
        # Create a list to hold the nodes
        nodes = []
       
        # Iterate through all legal moves
        for move in moves:
            # Create a fast clone of the current state
            nextState = currentState.fastclone()
           
            # Make the move on the cloned state
            nextState.makeMove(move)
           
            # Create a new Node object
            evaluation = self.utility(nextState) + 1
            node = Node(move=move, state=nextState, depth=1, evaluation=evaluation, parent=None)
           
            # Add the node to the list
            nodes.append(node)
       
        # Select the node with the highest evaluation using a helper method
        bestNode = self.getBestNode(nodes)
       
        # Return the move from the best node
        return bestNode.move

    ##
    # getBestNode
    # Description: Helper method to find the node with the highest evaluation from a list of nodes.
    # Parameters:
    #   nodes - A list of Node objects.
    # Return: The Node object with the highest evaluation.
    ##
    def getBestNode(self, nodes):
        if not nodes:
            return None
        
        bestNode = nodes[0]
        for node in nodes:
            # Check for a better evaluation
            if node.evaluation > bestNode.evaluation:
                bestNode = node
            # Simple tie-breaking to avoid cyclical behavior.
            elif node.evaluation == bestNode.evaluation and random.random() > 0.5:
                bestNode = node
        return bestNode
   
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
    #utility
    #Description: Returns a heuristic guess of how "good" a game state is
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #
    #Return: A utility value between 0 and 1
    ##
    def utility(self, currentState):
        # Get my and enemy's inventories
        myInv = currentState.inventories[self.playerId]
        enemyInv = currentState.inventories[1 - self.playerId]
       
        # Calculate scores
        # Score for food on my side
        food_score = myInv.foodCount - enemyInv.foodCount
       
        # Score for number of ants
        ant_score = len(myInv.ants) - len(enemyInv.ants)
       
        # Score for anthill health
        my_anthill_health = myInv.getAnthill().captureHealth
        enemy_anthill_health = enemyInv.getAnthill().captureHealth
        anthill_score = enemy_anthill_health - my_anthill_health
       
        # Score for tunnel health
        my_tunnels = getTunnels(myInv)
        enemy_tunnels = getTunnels(enemyInv)
        tunnel_score = 0
        if my_tunnels and enemy_tunnels:
            tunnel_score = enemy_tunnels[0].captureHealth - my_tunnels[0].captureHealth
       
        # Weighted sum of scores
        total_score = (food_score * 0.5) + (ant_score * 0.3) + (anthill_score * 0.2) + (tunnel_score * 0.1)
        
        # Normalize the score to a 0..1 range
        normalized_score = total_score / 10.0 + 0.5 
        
        # Clamp the value to be within 0 and 1
        return max(0, min(1, normalized_score))

    def registerWin(self, hasWon):
        pass