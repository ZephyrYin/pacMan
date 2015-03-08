# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
import sys
import copy

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]


        "*** YOUR CODE HERE ***"
        additionalScore = 0
        curPos = currentGameState.getPacmanPosition()
        nearestFood = self.getNearestFood(currentGameState)
        if len(nearestFood) > 0:
            nF = random.choice(nearestFood)
            curDistance = util.manhattanDistance(curPos, nF)
            newDistance = util.manhattanDistance(newPos, nF)
            if newDistance < curDistance:
                additionalScore += 1

        nearestFGhost = self.getNearestFrightenGhost(currentGameState)
        if len(nearestFGhost) > 0:
            nFG = random.choice(nearestFGhost)
            curDistance = util.manhattanDistance(curPos, nFG)
            newDistance = util.manhattanDistance(newPos, nFG)
            if newDistance < curDistance:
                additionalScore += 200                                          # go after the nearest frighten ghosts

        for gState in newGhostStates:
            if util.manhattanDistance(newPos, gState.getPosition()) == 1:
                if gState.scaredTimer == 0:
                    additionalScore -= 600                      # avoid be eaten by ghost

        return successorGameState.getScore() + additionalScore

    # add weight based on food and ghost:
    def getNearestFood(self, curGameState):
        pacManPos = curGameState.getPacmanPosition()
        food = curGameState.getFood()
        nearestFood = []

        minDistance = sys.maxint
        for f in food.asList():
            distance = util.manhattanDistance(pacManPos, f)
            if distance < minDistance:
                minDistance = distance
                nearestFood = []
                nearestFood.append(f)
            elif distance == minDistance:
                nearestFood.append(f)
        return nearestFood

    def getNearestFrightenGhost(self, curGameState):
        ghostStates = curGameState.getGhostStates()
        pacManPos = curGameState.getPacmanPosition()
        minDistance = sys.maxint

        nearestFGPos = []
        for ghostState in ghostStates:
            if ghostState.scaredTimer > 0:
                ghostPos = ghostState.getPosition()
                distance = util.manhattanDistance(pacManPos, ghostPos)
                if distance < minDistance:
                    minDistance = distance
                    nearestFGPos = []
                    nearestFGPos.append(ghostPos)
                elif distance == minDistance:
                    nearestFGPos.append(ghostPos)
        return nearestFGPos




def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        legalMoves = gameState.getLegalActions()
        legalMoves.remove(Directions.STOP)
        maxV = -sys.maxint - 1
        index = -1
        for i in range(len(legalMoves)):
            successorGameState = gameState.generatePacmanSuccessor(legalMoves[i])
            value = self.minValue(successorGameState, 0, self.depth)
            if value > maxV:
                maxV = value
                index = i
        if index >= 0:
            return legalMoves[index]


        #util.raiseNotDefined()

    def maxValue(self, gameState, curDepth, depthLimit):
        if curDepth > depthLimit or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        v = -sys.maxint - 1
        legalMoves = gameState.getLegalActions()
        legalMoves.remove(Directions.STOP)

        for action in legalMoves:
            successorGameState = gameState.generatePacmanSuccessor(action)
            v = max(v, self.minValue(successorGameState, curDepth, depthLimit))
        return v

    def minValue(self, gameState, curDepth, depthLimit):
        if curDepth > depthLimit or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)

        v = sys.maxint
        allMoves = []
        for agentIndex in range(1, gameState.getNumAgents()):
            legalMoves = gameState.getLegalActions(agentIndex)
            allMoves.append(legalMoves)
        actionPermutations = self.getPermutations(allMoves)

        for aP in actionPermutations:
            successorGameState = gameState.deepCopy()
            for index in range(len(aP)):
                successorGameState = successorGameState.generateSuccessor(index + 1, aP[index])
                if successorGameState.isLose() or successorGameState.isWin():
                    break
            v = min(v, self.maxValue(successorGameState, curDepth + 1, depthLimit))
        return v

    def getPermutations(self, a):
        result = []
        temp = []
        height = len(a)
        self.permutations(a, result, temp, 0, height)
        return result


    def permutations(self, a, result, temp, depth, height):
        if depth >= height:
            result.append(copy.deepcopy(temp))
            return
        for r in a[depth]:
            temp.append(r)
            self.permutations(a, result, temp, depth+1, height)
            temp.pop(-1)


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.

          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

