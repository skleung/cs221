AI Agents for Settlers of Catan
CS221 Final Project, Fall 2014
By: Sherman Leung, Sierra Kaplan-Nelson, Nick Troccoli
---------------------------
We wrote a couple different agents for this assignment (all against the baseline Random agent).
These agents are: Expectimax, Expectiminimax, and Monte-Carlo Tree Search (MCTS).

By default, you can play the MCTS agent vs. random by running:
`python settlers.py`

To change the number of iterations played, use the `-n` flag and a number to specify the number you want.

To run the Expectimax and the Expectiminimax agents, run
`python game.py -m`

By default, this will run the non-graphics, Expectimax vs. Random simulation.  To run Expectiminimax vs.
Random, please go into gameConstants.py and change the first number in DEFAULT_PLAYER_ARRAY from 11 to 12.
(11 is Expectimax, 12 is Expectiminimax).

By default the depth is set to 1 and the number of iterations are set to 10. Use the `-d` and the `-n` flag respectively to change these values.

To view the actions and the turn by turn summary associated with the game, add the -v flag.

To view the graphics associated with the game,  add the -g flag.
