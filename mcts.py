"""
A collection of classes and functions for playing certain types of
games. Specifically, an implementation of the MCTS algorithm.
"""
import random, Queue
from math import sqrt, log
from random import sample

from board import BeginnerLayout, Board, Edge, Hexagon, Vertex
from game import *
from agents import * 

VALUE_WIN = 1
VALUE_LOSE = -1

class MCTSGame(object):
    """
    Base class for multi-player adversarial games.
    """
    def actions(self, state, player):
        raise Exception('Method must be overridden.')

    def result(self, state, action, player):
        raise Exception('Method must be overridden.')

    def terminal(self, state):
        raise Exception('Method must be overridden.')

    def next_player(self, player):
        raise Exception('Method must be overridden.')

    def outcome(self, state, player):
        raise Exception('Method must be overridden.')


class Settlers(MCTSGame):
    """
    Wrapper implementation of the game Settlers of Catan, modeled as a tree search problem.

    An action is defined as a legal action determined by the gameState object in game.py
    """
    def __init__(self):
        self.players  = (0,1)
        self.game = Game()
        # Note that this initialization actually initializes both players to be alphaBeta agents
        self.game.initializePlayers()
        self.game.initializeSettlementsAndResourcesLumberBrick()

    def pretty_state(self, state):
        self.game.drawGame()

    def actions(self, state, player):
        return state.getLegalActions(player)

    def result(self, state, action, player):
        dieRoll = state.diceAgent.rollDice()
        state.updatePlayerResourcesForDiceRoll(dieRoll)
        return state.generateSuccessor(player, action)

    def terminal(self, state):
        # All columns full means we are done
        return state.gameOver() >= 0

    def next_player(self, player):
        if player not in self.players:
            raise Exception('Invalid player')
        index = self.players.index(player)
        if index < len(self.players) - 1:
            return self.players[index + 1]
        else:
            return self.players[0]
        
    def outcome(self, state, player):
        if state.gameOver() == player:
            return VALUE_WIN
        else:
            return VALUE_LOSE


class Node(object):

    COLORS = {
        1: 'red',
        2: 'yellow',
        3: 'orange',
        4: 'green',
        5: 'blue',
        6: 'purple'
    }

    def __init__(self, parent, action, state, player, game=None):
        if parent is None and game is None:
            raise Exception('No game provided')
        # Game
        self.game = game or parent.game
        # Structure
        self.parent    = parent
        self.children  = dict.fromkeys(self.game.actions(state, player))
        # Tree data
        self.action    = action
        self.state     = state
        # Search meta data
        self.player    = player
        self.visits    = 0
        self.value     = 0.0
    
    def __iter__(self):
        """
        A generator function. Does a pre-order traversal over the nodes
        in the tree without using recursion.
        """
        active = Queue.Queue()
        active.put(self)
        while active.qsize() > 0:
            next = active.get()
            for _, child in next.children.items():
                if child is not None:
                    active.put(child)
            yield next

    def __len__(self):
        """
        Returns the number of nodes in the tree. This requires a
        traversal, so it has O(n) running time.
        """
        n = 0
        for node in self.traverse():
            n += 1
        return n

    @property
    def weight(self):
        """
        The weight of the current node.
        """
        if self.visits == 0:
            return 0
        return self.value / float(self.visits)

    def search_weight(self, c):
        """
        Compute the UCT search weight function for this node. Defined as:

            w = Q(v') / N(v') + c * sqrt(2 * ln(N(v)) / N(v'))

        Where v' is the current node and v is the parent of the current node,
        and Q(x) is the total value of node x and N(x) is the number of visits
        to node x.
        """
        return self.weight + c * sqrt(2 * log(self.parent.visits) / self.visits)

    def actions(self):
        """
        The valid actions for the current node state.
        """
        return self.game.actions(self.state, self.player)

    def result(self, action):
        """
        The state resulting from the given action taken on the current node
        state by the node player.
        """
        return self.game.result(self.state, action, self.player)

    def terminal(self):
        """
        Whether the current node state is terminal.
        """
        return self.game.terminal(self.state)

    def next_player(self):
        """
        Returns the next game player given the current node's player.
        """
        return self.game.next_player(self.player)

    def outcome(self, player=None):
        """
        Returns the game outcome for the given player (default is the node's
        player) for the node state.
        """
        p = player or self.player
        return self.game.outcome(self.state, p)

    def fully_expanded(self):
        """
        Whether all child nodes have been expanded (instantiated). Essentially
        this just checks to see if any of its children are set to None.
        """
        return not None in self.children.values()

    def expand(self):
        """
        Instantiates one of the unexpanded children (if there are any,
        otherwise raises an exception) and returns it.
        """
        try:
            action = self.children.keys()[self.children.values().index(None)]
        except ValueError:
            raise Exception('Node is already fully expanded')

        state = self.game.result(self.state, action, self.player)
        player = self.game.next_player(self.player)

        child = Node(self, action, state, player)
        self.children[action] = child
        return child

    def best_child(self, c=1/sqrt(2)):
        if not self.fully_expanded():
            raise Exception('Node is not fully expanded')
        return max(self.children.values(), key=lambda x: x.search_weight(c))
        
    def best_action(self, c=1/sqrt(2)):
        """
        Returns the action needed to reach the best child from the current
        node.
        """
        return self.best_child(c).action

    def max_child(self):
        """
        Returns the child with the highest value.
        """
        return max(self.children.values(), key=lambda x: x.weight)

    def simulation(self, player):
        """
        Simulates the game to completion, choosing moves in a uniformly random
        manner. The outcome of the simulation is returns as the state value for
        the given player.
        """
        st = self.state
        pl = self.player
        while not self.game.terminal(st):
            action = None
            if len(self.game.actions(st, pl)) > 0:
                action = sample(self.game.actions(st, pl), 1)[0]
            st = self.game.result(st, action, pl)
            # update resources here!

            pl = self.game.next_player(pl)
        return self.game.outcome(st, player)
        
    def dot_string(self, value=False, prettify=lambda x: x):
        """
        Returns the tree rooted at the current node as a string
        in dot format. Each node is labeled with its state, which
        is first run through prettify. If value is True, then
        the value is included in the node label.
        """
        output = ''
        output += 'digraph {\n'
        for node in self:
            # Define the node
            name = prettify(node.state)
            if value:
                name += '%s\\n' % node.value
            color = self.COLORS[node.player]
            output += '\t"%s" [style="filled", fillcolor="%s"]\n' % (
                name, color
            )
            # No edge into the root node
            if node.parent is None:
                continue
            # Add edge from node parent to node
            pname = prettify(node.parent.state)
            if value:
                pname += '%s\\n' % node.parent.value
            output += '\t"%s" -> "%s"\n' % (pname, name)
        output += '}'
        return output


def mcts_uct(game, state, player, budget):
    """
    Implementation of the UCT variant of the MCTS algorithm.
    """
    root = Node(None, None, state, player, game)
    while budget:
        budget -= 1
        # Tree Policy
        child = root
        while not child.terminal():
            if not child.fully_expanded():
                child = child.expand()
                break
            else:
                child = child.best_child()
        # Default Policy
        delta = child.simulation(player)
        # Backup
        while not child is None:
            child.visits += 1
            child.value += delta
            child = child.parent

    return root.best_action(c=0)


def full_tree(game, state, player):
    """
    Creates a full game tree in which player moves first. The traversal is done
    in breadth-first order. The return value is the root node.
    """
    active = Queue.Queue()
    root = Node(None, None, state, player)
    active.put(root)
    
    current = None
    while active.qsize() > 0:
        current = active.get()  
        # Assign value if this is a terminal node
        if game.terminal(current.state):
            continue
        # Explore children otherwise
        for action in game.actions(current.state, current.player
                                   ):
            nstate = game.result(current.state, action, current.player)
            nplayer = game.next_player(current.player)
            node = Node(current, action, nstate, nplayer)
            current.children[action] = node
            active.put(node)
    return root


def minimax(game, state, player):
    """
    Applies the Minimax algorithm to the given game. Returns the
    root node with values assigned to each node in the game tree.
    """
    active = []
    
    root = full_tree(game, state, player)
    for node in root:
        active.append(node)
    
    current = None
    while active:
        current = active.pop()
        # Leaf (terminal) node
        if game.terminal(current.state):
            current.value = game.outcome(current.state, player)
            continue
        # Interior or root node
        values = tuple([i.value for i in current.children.values()])
        if current.player == player:
            current.value = max(values)
        else:
            current.value = min(values)
    
    return root


def mcts(game, state, player, n):
    """
    Implementation of the UCT variant of the Monte Carlo Tree Search algorithm.
    """
    root = Node(None, None, state, player)
    unexplored = Queue.Queue()
    unexplored.put(root)

    for _ in xrange(n):
        # Quit early if we are out of nodes
        if unexplored.qsize() == 0:
            break
        # Add the new node to the tree
        current = unexplored.get()
        if current.parent is not None:
            current.parent.children[current.action] = current
        # Add the newly discovered nodes to the queue
        for action in game.actions(current.state, current.player):
            nstate = game.result(current.state, action, current.player)
            nplayer = game.next_player(current.player)
            node = Node(current, action, nstate, nplayer)
            unexplored.put(node)
        # Simulate the rest of the game from the current node
        cstate = current.state
        cplayer = current.player
        while not game.terminal(cstate):
            caction = random.choice(game.actions(cstate, cplayer))
            cstate = game.result(cstate, caction, cplayer)
            cplayer = game.next_player(cplayer)
        simvalue = game.outcome(cstate, player)
        # Back simulation value up to the root
        backup = current
        while backup is not None:
            backup.value += simvalue
            backup.visits += 1
            backup = backup.parent

    return root
