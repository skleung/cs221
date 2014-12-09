import sys
import mcts
import random
import time

def play(n=100, human=False, randomFlag=True):
# Testing ConnectFour - mcts_uct()
    game = mcts.Settlers()
    state = game.game.gameState
    player = game.players[0]
    computer = game.players[1]
    graphics = False
    while not game.terminal(state):
        if graphics: game.pretty_state(state)
        if human:
            prompt = 'Choose a move, choices are %s: ' % (game.actions(state, player))
            success = False
            while not success:
                choice = raw_input(prompt)
                try:
                    action = int(choice)
                    state = game.result(state, action, player)
                    success = True
                except ValueError:
                    pass
                except Exception:
                    pass
        elif randomFlag:
            actions = game.actions(state, player)
            action = random.choice(actions)
            state = game.result(state, action, player)
        # defaults to MCTS agent...
        else:
            action = mcts.mcts_uct(game, state, player, n)
            state = game.result(state, action, player)
        print 'Player 1 chose ' + str(action)
        if graphics: game.pretty_state(state)

        # Intermediate win check
        if game.terminal(state):
            break

        # Computer plays now
        ts = time.time()
        action = mcts.mcts_uct(game, state, computer, n)
        state = game.result(state, action, computer)

        print 'Player 2 (MCTS) chose ' + str(action) + " (elapsed time="+str(time.time()-ts)+")"

    if graphics: game.pretty_state(state)
    print
    outcome = game.outcome(state, player)
    if outcome == 1:
        print 'Player 1 wins.'
    elif outcome == -1:
        print 'Player 2 wins.'
    else:
        print 'Tie game.'
    

n = 100
if len(sys.argv) > 1:
    try:
        n = int(sys.argv[1])
    except ValueError:
        pass

n = 100
if '-n' in sys.argv:
    try:
        n = int(sys.argv[sys.argv.index('-n') + 1])
    except:
        pass

human = False
if '-c' in sys.argv:
    human = False

randomFlag = False
if '-r' in sys.argv:
    randomFlag = True


START_TIME = time.time()
print 'Number of Sample Iterations: ' + str(n)
print 'Human Player: ' + str(human)
print 'Random Player: ' + str(randomFlag)
play(n=n, human=human, randomFlag=randomFlag)
print "time elapsed = "+str(time.time()-START_TIME)
