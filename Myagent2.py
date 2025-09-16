import random
import sys
import unittest
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
        super(AIPlayer,self).__init__(inputPlayerId, "Random")
   
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
        myAnthills = getConstrList(currentState, pid=self.playerId, types=(ANTHILL,))
        enemyAnthills = getConstrList(currentState, pid=1 - self.playerId, types=(ANTHILL,))

        my_anthill_health = myAnthills[0].captureHealth if myAnthills else 0
        enemy_anthill_health = enemyAnthills[0].captureHealth if enemyAnthills else 0

        anthill_score = enemy_anthill_health - my_anthill_health
       
        # Score for tunnel health
        my_tunnels = Inventory.getTunnels(myInv)
        enemy_tunnels = Inventory.getTunnels(enemyInv)
        tunnel_score = 0
        if my_tunnels and enemy_tunnels:
            tunnel_score = enemy_tunnels[0].captureHealth - my_tunnels[0].captureHealth
       
        # Weighted sum of scores
        total_score = (food_score * 0.5) + (ant_score * 0.3) + (anthill_score * 0.2) + (tunnel_score * 0.1)
        
        # Normalize the score to a 0..1 range
        normalized_score = total_score / 10.0 + 0.5 
        
        # Clamp the value to be within 0 and 1
        return max(0, min(1, normalized_score))

    def createNode(self,parentNode,move):
    
        # move parent to next state
        nextState = getNextState(parentNode, move)
        
        # how many moves away next state is from current state
        depth = 1

        # evaluate next state
        evaluation = self.utility(nextState)


        # return node as dictionary
        return {
            'move':move,
            'state':nextState,
            'depth':depth,
            'evaluation':evaluation,
            'parent': parentNode
        }
    
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
        nodes = []

        for move in moves:
            nextState = getNextState(currentState, move)
            evaluation = self.utility(nextState)
            node = Node(move=move, state=nextState, depth=1, evaluation=evaluation, parent=None)
            nodes.append(node)

        bestNode = self.getBestNode(nodes)
        return bestNode.move if bestNode else Move(END, None, None)


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
    
    def registerWin(self, hasWon):
        pass

    @staticmethod
    def makeTestState():
        return GameState.getBasicState()

class TestAIPlayer(unittest.TestCase):
    # create mock test set up
    def setUp(self):
        # mock ai
        self.agent = AIPlayer(0)
        # mock game state
        self.state = AIPlayer.makeTestState()

# utility function should return a value between 0-1
def test_utility_range(self):
    score = self.agent.utility(self.state)
    
    # score is not below 0
    self.assertGreaterEqual(score, 0)
    
    # score is not above 1
    self.assertLessEqual(score, 1)

# createNode should return a valid dictionary
def test_create_node_structure(self):
    # mock move
    move = Move(MOVE_ANT, (0, 0), (1, 1))
    
    # create node from the current state and move
    node = self.agent.createNode(self.state, move)
    
    # ensure all keys are in dictionary
    self.assertIn('move', node)
    self.assertIn('state', node)
    self.assertIn('evaluation', node)
    self.assertIn('depth', node)
    self.assertIn('parent', node)

# getBestNode should select node with highest utility
def test_best_node_selection(self):
    # generate two mock moves
    move1 = Move(MOVE_ANT, (0, 0), (1, 1))
    move2 = Move(MOVE_ANT, (0, 0), (2, 2))
    
    # get next state from each move
    state1 = getNextState(self.state, move1)
    state2 = getNextState(self.state, move2)
    
    # create nodes with utility scores
    node1 = Node(move1, state1, 1, self.agent.utility(state1), None)
    node2 = Node(move2, state2, 1, self.agent.utility(state2), None)
    
    # use bestNode to get highest score
    best = self.agent.getBestNode([node1, node2])
    
    # ensure it's a valid node
    self.assertIsInstance(best, Node)
    
    # ensure it's a valid move
    self.assertIn(best.move, [move1, move2])




if __name__ == "__main__":
    unittest.main()
