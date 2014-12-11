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

    numTurns = 0
    while not game.terminal(state):
        numTurns += 1
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
            print 'Player 1 (Human) chose ' + str(action)
        elif randomFlag:
            actions = game.actions(state, player)
            action = random.choice(actions)
            state = game.result(state, action, player)
            print 'Player 1 (Random) chose ' + str(action)
        # defaults to Minimax agent...
        else:
            action = state.playerAgents[player].getAction(state)
            state = game.result(state, action, player)
            print 'Player 1 (Expectiminimax) chose ' + str(action)
        
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
    ptDeficit = abs(state.playerAgents[0].victoryPoints - state.playerAgents[1].victoryPoints)
    if outcome == 1:
        print 'Player 1 wins.'
        return (1, numTurns, ptDeficit)
    elif outcome == -1:
        print 'Player 2 (MCTS) wins.'
        return (2, numTurns, ptDeficit)
    else:
        print 'Tie game.'
    return (0, numTurns, ptDeficit)
    

n = 20
if len(sys.argv) > 1:
    try:
        n = int(sys.argv[1])
    except ValueError:
        pass

n = 20
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
print 'Number of Total Iterations: ' + str(n)
print 'Number of Sample simulations for MCTS algorithm: ' + str(50)
print 'Who is the first player?'
print 'Human Player: ' + str(human)
print 'Random Player: ' + str(randomFlag)
print 'Expectimax Player: ' + str(not randomFlag)


mctsWins = 0
mctsTurns = []
mctsTimes = []
mctsPtDeficit = []

randomWins = 0
randomTurns = []
randomTimes = []
randomPtDeficit= []

weirdGames = 0
for i in range(n):
    whoWon = 0
    nTurns = 0
    ptDeficit = 0
    startTime = time.time()
    try:
        # Note: I'm hardcoding our number of sample iterations to 50 here!
        whoWon, nTurns, ptDeficit = play(n=50, human=human, randomFlag=randomFlag)
    except Exception:
        whoWon = 0
        print "EXCEPTION WAS THROWN"
        pass
    timeElapsed = time.time()-startTime
    print "Game #"+str(i)+": time elapsed = "+str(timeElapsed)
    if (whoWon == 2):
        mctsWins += 1
        mctsTurns.append(nTurns)
        mctsTimes.append(timeElapsed)
        mctsPtDeficit.append(ptDeficit)
    elif (whoWon == 1):
        randomWins += 1
        randomTurns.append(nTurns)
        randomTimes.append(timeElapsed)
        randomPtDeficit.append(ptDeficit)
    else:
        weirdGames += 1

def getAvg(arr):
    if len(arr) == 0:
        return "0"
    return str(sum(arr)/float(len(arr)))
print "===================="
print "Overall statistics: "
print str(mctsWins) + " wins for MCTS"
print "Average time to win for MCTS =" + getAvg(mctsTimes)
print "Average turns to win for MCTS =" + getAvg(mctsTurns)
print "Average ptDecifit to win for MCTS =" + getAvg(mctsPtDeficit)

print str(randomWins) + " wins for Random player"
print "Average time to win for Random player =" + getAvg(randomTimes)
print "Average turns to win for Random player =" + getAvg(randomTurns)
print "Average ptDecifit to win for Random player =" + getAvg(randomPtDeficit)
print


print str(weirdGames) + " weird games happened"
print str(mctsWins/float(mctsWins+randomWins)) +" %% win rate by MCTS agent"
